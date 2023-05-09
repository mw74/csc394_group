from django.shortcuts import render
from django.http import HttpResponse
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

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

def index(request):
    return render(request, "index.html")

def process_form(request):
    if request.method == 'POST':
        name = request.POST['name']
        location = request.POST['location']
        interest = request.POST['interest']
        time_of_day = request.POST['timeOfDay']
        trip_planner = TripPlanner(str(api_key))
        response = trip_planner.plan_trip(name, location, interest, time_of_day)
        context = {'response_string' : str(response)}
        print(str(response))
        return render(request, 'response.html', context)
    return render(request, 'index.html')


class TripPlanner:

    def __init__(self, api_key):
        self.api_key = api_key

    def plan_trip(self, user_name, user_location, user_interest, user_timeofday):
        # Create and write the user input to a new text file
        directory = "src/prompt"
        filename = "user_input.txt"
        file_path = os.path.join(directory, filename)

        prompt = f"Hi, my name is {user_name} and I live in {user_location}. \
        I enjoy {user_interest} and I am looking for activities in the {user_timeofday}"

        with open(file_path, "w") as file:
            file.write(prompt)

        documents = SimpleDirectoryReader(directory).load_data()

        llm_predictor = LLMPredictor(llm=ChatOpenAI(openai_api_key=self.api_key,
                                               model_name="gpt-3.5-turbo",
                                               temperature=1.0,
                                               top_p=1.0,
                                               frequency_penalty=0.5,
                                               presence_penalty=1.0,
                                               max_tokens=1024))

        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

        davinci_index = GPTListIndex.from_documents(documents, service_context=service_context)

        response = davinci_index.query("Please plan a trip this summer that cites specific events and attractions including pricing and where to get tickets. Stay focused on the given location. Always address me by first name and respond in an incredibly friendly manner.")

        return response
