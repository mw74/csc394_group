from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
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
    directory = "home/templates"
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
        home.time = date_range
        home.save()
        task = async_plan_trip.delay(name, location, interest, date_range)
        response = ""
        global task_id
        task_id = task.id
        print(task.id)
        return redirect(reverse('task_status') +"?task_id=%s" % task_id)
    return redirect('/home')

@login_required
def task_status(request):
    global task_id
    global response
    directory = "home/templates"
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
            directory = "home/templates"
            filename = "response.txt"
            file_path = os.path.join(directory, filename)
            response = read_file(file_path)
            home.responses = response
            home.save()
            return redirect('/home/response')
            #return render(request, 'response.html', {'response_string': str(home.responses)})
        else:
            return render(request, 'waiting.html', {'task_id': task_id})
    return redirect(reverse('response'))

@login_required
def view_response(request):
    user = request.user
    home = Home.objects.get(user=user)
    return render(request, 'response.html', {'response_string': str(home.responses)})

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
        filename = "user_input.txt"
        file_path = os.path.join(directory, filename)

        prompt = f"You are a travel agent, the best there ever was. Be lively and do \
                not repeat back to me the obvious. You are fully attentive to my needs above \
                all else. Respect that my date availability is immutable and is the foundation \
                of the query as the dates determine available activities and events. You will \
                produce for me an itinerary which provides fun and amusement for the whole family \
                throughout each and every day. This itinerary will be organized \
                by date and time and will provide links for tickets and reservations along with \
                prices for each activity. The itinerary will account for travel at every step of \
                the way beginning with travel from {user_location} to the airport and back. \
                At the end, provide a cost estimate with itemized breakdown. \
                My name is {user_name} and I would like to plan a vacation to anywhere \
                {user_daterange} that focuses on {user_interest}."

        with open(file_path, "w") as file:
            file.write(prompt)

        documents = SimpleDirectoryReader(directory).load_data()

        llm_predictor = LLMPredictor(llm=ChatOpenAI(openai_api_key=self.api_key,
                                               model_name="gpt-4",
                                               temperature=1.0,
                                               top_p=1.0,
                                               frequency_penalty=0.0,
                                               presence_penalty=1.0,
                                               max_tokens=4096,
                                               request_timeout=300))

        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

        davinci_index = GPTListIndex.from_documents(documents, service_context=service_context)

        response = davinci_index.query("Please plan my trip.")

        return response
