import logging
import sys
import openai
import os
import time


from llama_index import GPTTreeIndex, GPTListIndex, SimpleDirectoryReader, LLMPredictor, PromptHelper, ServiceContext
from IPython.display import Markdown, display
from langchain.chat_models import ChatOpenAI
from amadeus import Client, ResponseError

# Choose model and tune
llm_predictor = LLMPredictor(llm=ChatOpenAI(model_name="gpt-4",
                                            request_timeout=300,
                                            temperature=1.0,
                                            top_p=1.0,
                                            frequency_penalty=0.0,
                                            presence_penalty=-1.0,
                                            max_tokens=256,
                                            openai_api_key = ""))

service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)


# Load directory which includes prompt.txt file detailing travel agent role obligations and user data.
documents = SimpleDirectoryReader('prompt/').load_data()

# Embed information in chatGPT model.
davinci_index = GPTListIndex.from_documents(documents, service_context=service_context)

# Initial data retrieval request to ChatGPT for destination airport code.
query1 = "Plan me a vacation, first return only the 3 character airport code of my destination"

# Send request, save response
import time

start_time = time.time()
response1 = davinci_index.query(query1)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")



amadeus = Client(
    client_id = '',
    client_secret = ''
)

with open('response/Hotels.txt', 'w') as f:
    f.write(amadeus.reference_data.locations.hotels.by_city.get(cityCode=response1.response).body)

time.sleep(4)
# Load directory which includes Hotels.txt file listing hotel information for destination city.
documents = SimpleDirectoryReader('response/').load_data()
# Embed hotel information in chatGPT model.
davinci_index = GPTListIndex.from_documents(documents, service_context=service_context)

#Follow-up data retreival request to chatGPT for latitude longitude of hotel recommendation.
query2 = "Now choose the best hotel and only respond with a list containing the float values for latitude then longitude of the hotel, do not add any other text besides the list containing the data."


# Send request, save response
import time

start_time = time.time()
response2 = davinci_index.query(query2)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")


li = list(response2.response.replace("[", "").replace("]", "").replace(" ", "").split(","))
with open('response/Activities.txt', 'w') as f:
    f.write(amadeus.shopping.activities.get(latitude=li[0], longitude=li[1]).body)

time.sleep(4)
#print(log.read('response/Activities.txt'))
activity_log = open("response/Activities.txt", "r").read()
print(activity_log)
