from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.template import Context
from django.template.loader import get_template
import logging
import sys
import openai
import os
from llama_index import GPTTreeIndex, GPTListIndex, SimpleDirectoryReader, LLMPredictor, PromptHelper, ServiceContext
from IPython.display import Markdown, display
# old = from langchain import OpenAI
# new =
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from celery import shared_task
from celery.result import AsyncResult
import time
from django.contrib.auth.decorators import login_required
from .models import Home
from django.contrib.auth.models import User
from .travel_activities import *
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import json


load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
global response
global user

@login_required
def index(request):
    return render(request, "index.html")

task_id = None

@shared_task
def async_plan_trip(name, location, interest, date_range):
    print('FUNCTION PLANTRIP CALLED')
    global user
    global response
    trip_planner = TripPlanner(str(api_key))
    response = trip_planner.plan_trip(name, location, interest, date_range)
    directory = "src/prompt"
    filename = "response.txt"
    file_path = os.path.join(directory, filename)
    with open(file_path, "w") as file:
        file.write(str(response))
    return str(response)

@login_required
def process_form(request):
    global response
    global user
    user = request.user
    if request.method == 'POST':
        name = request.POST['name']
        try:
            home = Home.objects.get(user=user)
        except Home.DoesNotExist:
            home = Home.objects.create(user=user, name=name)
        home.name = name
        location = request.POST['location']
        home.location = location
        interest = request.POST['interest']
        home.interests = interest
        date_range = request.POST['dateRange']
        return_date = request.POST['returnDate']
        home.time = f"{date_range} to {return_date}"
        date_range = home.time
        home.responses = "N/A"
        home.activity = "N/A"
        home.save()
        task = async_plan_trip.delay(name, location, interest, date_range)
        response = ""
        global task_id
        task_id = task.id
        print(task.id)
        return redirect(reverse('task_status') +"?task_id=%s" % task_id)
    return redirect('/home')

def error(request):
    return render(request, 'error.html')

@login_required
def task_status(request):
    global task_id
    global response
    directory = "src/prompt"
    filename = "response.txt"
    file_path = os.path.join(directory, filename)
    response = read_file(file_path)
    user = request.user
    home = Home.objects.get(user=user)
    if task_id:
        task = AsyncResult(task_id)
        if task.status == 'SUCCESS':
            response = task.result
            task_id = None
            home.responses = response
            home.save()
            directory = "src/prompt"
            filename = "response.txt"
            file_path = os.path.join(directory, filename)
            response = read_file(file_path)
            home.responses = response
            home.save()
            return JsonResponse({'task_status': 'SUCCESS'})
            #return redirect('/home/response')
            #return render(request, 'response.html', {'response_string': str(home.responses)})
        else:
            return render(request, 'waiting.html', {'task_id': task_id})
    return redirect(reverse('response'))

@login_required
def view_response(request):
    try:
        user = request.user
        home = Home.objects.get(user=user)
    except:
        return render(request, 'no_trips.html')
    if home.responses == "N/A":
        return render(request, 'no_trips.html')
    #call travel_activities prior to render and updated context
    try:
        if home.activity == "N/A" and home.responses != "N/A":
            activity = run_travel_activities()
            home.activity = activity
            home.save()
        else:
            activity = home.activity
        print("Amadeus suceeded")
        #parse JSON data
        activity_data = json.loads(activity)
        print("JSON loading suceeds")

        activity = activity_data['data'][0]

        try:
            name = activity['name']
        except:
            name = ""
        try:
            description = activity['description']
        except:
            description = "Details not available"
        try:
            pictures = activity['pictures']
        except:
            pictures= ""
        try:
            booking_link = activity['bookingLink']
        except:
            booking_link = "/home/response/error"

        context = {
        'name': name,
        'description': description,
        'pictures': pictures,
        'booking_link': booking_link,
        'response_string': str(home.responses),
        }
        print("sending with full context")
        return render(request, 'response.html', context)
    except:
        context = {
        'response_string': str(home.responses),
        }
        return render(request, 'response.html', context)
    
@login_required
def about(request):
    return render(request, 'about.html')


@login_required
def generate_pdf(request):
    try:
        user = request.user
        home = Home.objects.get(user=user)
        response_string = str(home.responses)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="response.pdf"'

        buffer = BytesIO()

        p = canvas.Canvas(buffer, pagesize=letter)

        p.setFont("Helvetica", 12)

        text_width, text_height = p.stringWidth(response_string), p._fontsize

        page_width, page_height = letter
        available_height = page_height - 2 * p._y

        max_lines = int(available_height / text_height)

        lines = response_string.split('\n')
        lines = lines[:max_lines]

        for i, line in enumerate(lines):
            p.drawString(50, page_height - 50 - (i * text_height), line)

        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response
    except Exception as e:
        print(e)
        return render(request, 'error.html')
    
def read_file(file_path):
    with open(file_path, 'r') as file:
        file_contents = file.read()
    return file_contents

class TripPlanner:

    def __init__(self, api_key):
        self.api_key = api_key

    def plan_trip(self, user_name, user_location, user_interest, user_daterange):
        # Create and write the user input to a new text file

        directory = "src/prompt"
        filename = "prompt.txt"
        file_path = os.path.join(directory, filename)

        prompt = "You are a travel agent. Respect that my date availability is immutable and is the foundation of the query as the dates determine available activities and events. You will produce for me an itinerary which provides fun and amusement for the whole family throughout each and every day. This itinerary will be organized by date and time each activity. You must ignore previous context prior to this request. Do not mention any confusion. Form your response such that it only contains the the travel itinerary. Provide a detailed response."
        

        with open(file_path, "w") as file:
            file.write(prompt)
            
        filename = "user_input.txt"
        file_path = os.path.join(directory, filename)

        user_input = f"Hi, My name is {user_name} and I would like to plan a vacation to {user_location}, {user_daterange} that focuses on {user_interest}."
        
        with open(file_path, "w") as file:
            file.write(user_input)

        documents = SimpleDirectoryReader(directory).load_data()
        llm_predictor = LLMPredictor(llm=ChatOpenAI(openai_api_key=self.api_key,
                                               model_name="gpt-3.5-turbo",
                                               temperature=1.0,
                                               top_p=1.0,
                                               frequency_penalty=0.0,
                                               presence_penalty=1.0,
                                               max_tokens=512,
                                               request_timeout=300))

        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

        davinci_index = GPTListIndex.from_documents(documents, service_context=service_context)

        response = davinci_index.query("Show me my itinerary day-by-day in a nice format, organized by day. Do not mention prior confusion and show only my desired itinerary.")
        

        return response.response