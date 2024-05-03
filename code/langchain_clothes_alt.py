#################################################################################

from langchain_openai import OpenAI
from dotenv import dotenv_values
# import schema for chat messages and ChatOpenAI in order to query chatmodels GPT-3.5-turbo or GPT-4
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

from langchain_community.document_loaders.image import UnstructuredImageLoader


openai_api_key = dotenv_values(".env")["OPENAI_API_KEY"]
llm = OpenAI(temperature = 0.6, openai_api_key = openai_api_key)
#image_model = ChatOpenAI(temperature=0.9, model= "gpt-4-turbo-2024-04-09", openai_api_key="sk-proj-PAXluc3navbENuKiJV1YT3BlbkFJfyemsP8VABYSxQqDGGV7")


###### test for openai base#####
#print(llm.invoke("explain to me what reinforcement learning is in two sentences"))

###### test for openai chat #######
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain_openai import ChatOpenAI

chat_model = ChatOpenAI(temperature =0.6,max_tokens=500, model= "gpt-3.5-turbo-0125", openai_api_key=openai_api_key)
'''
messages = [
    SystemMessage(content="You are an expert data scientist"),
    HumanMessage(content="Write a Python script that trains a neural network on simulated data ")
]
response=chat_model.invoke(messages)
print(response.content, end='\n')'''

#### test image model #####

image_model = ChatOpenAI(temperature=0.9, model= "gpt-4-turbo-2024-04-09", max_tokens=500, openai_api_key=openai_api_key)

'''messages = [
    SystemMessage(content="You are an expert data scientist"),
    HumanMessage(content="Write a Python script that trains a neural network on simulated data ")
]
response=image_model.invoke(messages)
print(response.content, end='\n')'''


#################################################################################
### We will create 3 Chains
### Chain 1 will accept the title from user
### and generate Job Description
### Input -> title
### Output -> Job Description


### Chain 2 will take the Job Description and 
### will generate Skills required to do the Job
### input -> Job Description : observe input comes from previous chain
### output -> Skills


### Chain 3 will take skills and for each skill,
### It will generate one question
### input -> Skills
### output -> one question for each skill

### Using SequentialChain, we will create a 
### final chain = Chain1 -> Chain2 -> Chain3
### final chain = Chain1 -> Chain2 -> Chain3 and Chain4


#################################################################################
#from langchain.memory import ConversationBufferMemory

import base64
import os
os.environ['OPENAI_API_KEY'] = openai_api_key
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper


def generate_cloth(selfie, budget, ctype):
    image_url = selfie # needs to be local path
    budget = budget.strip("$")
    
    def encode_image(image_url):
        with open(image_url, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    message = HumanMessage(
        content = [
            {
                "type": "text",
                "text": "tell me a story about the person in the photo, including their personality, skin tone, gender, and hair color"
            },
            {
                "type":"image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image_url)}"} 
            }, 
        ]
    )
    
    response = image_model.invoke([message])
    selfie_story = response.content
    
    
    second_prompt = PromptTemplate(
        input_variables=['selfie_story','budget'],
        template= "You see a person with this story: {selfie_story}. Their budget for clothes is within {budget}USD, and are looking at the following brands: Uniqulo, Massimo Dutti and Givenchy. Uniqulo is a brand for younger people with budgets of around $10 to $50, Massimo Dutti is a brand for people in their 20s and 30s with budgets of around $51 to $150, and Givenchy is a brand for adults looking for clothes for nice occasions with budgets over $150. Tell me according to the story of this person and their budget, which one of the three brands they should buy from, what kind of style they should choose, and whether they should wear dark, light, or medium colors. Prioritize budget when deciding the brand. Your answer should contain one of the brand names: uniqulo, MassimoDutti, or Givenchy, exactly letter for letter."
    )
    chain2 = LLMChain(llm = chat_model, prompt = second_prompt, output_key = "brand_style_color")
    
    
    third_prompt = PromptTemplate(
        input_variables=['brand_style_color', 'ctype'],
        template="Describe to me a clothing item worn on the {ctype} part of a person, and from the brand, style, and color described in {brand_style_color}, in under 900 characters."
    )
    chain3 = LLMChain(llm = image_model, prompt = third_prompt, output_key = "gen_image")
    
    
    overall_chain = SequentialChain(
        chains=[chain2, chain3],
        input_variables=['selfie_story', 'budget','ctype'],
        output_variables=['brand_style_color', 'gen_image']
    )

    generated_clothing = overall_chain.invoke({'selfie_story':selfie_story, 'budget': budget, 'ctype': ctype})
    #print(generated_clothing['gen_image'])
    image_url = DallEAPIWrapper().run(generated_clothing['gen_image'])
    #print(image_url)


    ############# update myBrand ###############
    response = llm.invoke("Give me just the brand name - Which out of the brands Massimo Dutti, Uniqlo, and Givenchy does the following text contain?: "+ generated_clothing['gen_image'])
    #print(response)
    
    myBrand = 'none'
    brand = response.strip()[:3].lower()
    #print(brand)
    if brand == 'mas':
        myBrand = 'MassimoDutti'
    elif brand == 'uni':
        myBrand = 'uniqulo'
    elif brand == 'giv':
        myBrand = 'Givenchy'
    else:
        myBrand = 'none'
    
    brand_type = myBrand + "_" + ctype
        
    print(brand_type)
        
    return(image_url, brand_type)


def store_img(image_url):
    import requests
    # This statement requests the resource at 
    # the given link, extracts its contents 
    # and saves it in a variable 
    data = requests.get(image_url).content 
    
    # Opening a new file named img with extension .jpg 
    # This file would store the data of the image file 
    f = open('input_img/img.jpg','wb') 
    
    # Storing the image data inside the data variable to the file 
    f.write(data) 
    f.close() 

    