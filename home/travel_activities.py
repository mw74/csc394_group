import logging
import sys
import openai
import os
import time
from llama_index import GPTTreeIndex, GPTListIndex, SimpleDirectoryReader, LLMPredictor, PromptHelper, ServiceContext
from IPython.display import Markdown, display
from langchain.chat_models import ChatOpenAI
from amadeus import Client, ResponseError
from dotenv import load_dotenv


def run_travel_activities():
    load_dotenv()

    api_key = os.getenv('OPENAI_API_KEY')

    # Choose model and tune
    llm_predictor = LLMPredictor(llm=ChatOpenAI(model_name="gpt-4",
                                                request_timeout=300,
                                                temperature=1.0,
                                                top_p=1.0,
                                                frequency_penalty=0.0,
                                                presence_penalty=-1.0,
                                                max_tokens=256,
                                                openai_api_key=api_key))

    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

    # Load directory which includes prompt.txt file detailing travel agent role obligations and user data.
    documents = SimpleDirectoryReader('src/prompt/').load_data()  # Updated to pull data from User model

    # Embed information in chatGPT model.
    davinci_index = GPTListIndex.from_documents(documents, service_context=service_context)

    # Initial data retrieval request to ChatGPT for destination airport code.
    query1 = "Plan me a vacation based on the destination provided and described, first return only the 3 character airport code of my destination only. And nothing else."

    # Send request, save response
    start_time = time.time()
    response1 = davinci_index.query(query1)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

    amadeus = Client(
        client_id=os.getenv('AMADEUS_API_KEY'),
        client_secret=os.getenv('AMADEUS_API_SECRET')
    )

    with open('src/response/Hotels.txt', 'w') as f:
        f.write(amadeus.reference_data.locations.hotels.by_city.get(cityCode=response1.response).body)

    time.sleep(6)
    # Load directory which includes Hotels.txt file listing hotel information for destination city.
    documents = SimpleDirectoryReader('src/response/').load_data()
    # Embed hotel information in chatGPT model.
    davinci_index = GPTListIndex.from_documents(documents, service_context=service_context)

    # Follow-up data retrieval request to chatGPT for latitude longitude of hotel recommendation.
    query2 = "Now choose the best hotel and only respond with a list containing the float values for latitude then longitude of the hotel, do not add any other text besides the list containing the data."

    # Send request, save response
    start_time = time.time()
    response2 = davinci_index.query(query2)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

    print(response2)
    li = list(response2.response.replace("[", "").replace("]", "").replace(" ", "").split(","))
    with open('src/response/Activities.txt', 'w') as f:
        f.write(amadeus.shopping.activities.get(latitude=li[0], longitude=li[1]).body)

    time.sleep(6)
    # print(log.read('response/Activities.txt'))
    activity_log = open("src/response/Activities.txt", "r").read()
    return activity_log


