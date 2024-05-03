import os
import numpy as np
from PIL import Image
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from pinecone import Pinecone
import pandas as pd
import requests
from dotenv import dotenv_values

def get_image_embedding(image_path,model):
    # Load and preprocess the image
    img = image.load_img(image_path, target_size=(150, 120))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # Obtain the image embedding
    embedding = model.predict(img_array)
    return embedding.flatten()

def query_cloth(input_img: str, brand_type: str, model ):
    pinecone_api_key= dotenv_values(".env")["pinecone_api_key"]

    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index('imagevector')

    # Make a single call to the API 
    q_responses = get_image_embedding(input_img,model).tolist()

    # time to query
    result = index.query(
        namespace= brand_type,
        vector = q_responses,
        top_k = 3
    )

    # Extract IDs from the 'matches' list in the dictionary
    ids_list = [match['id'] for match in result.to_dict()['matches']]

    return ids_list 

def read_image(image_ids:list, brand_type:str ):
# Split brand_type into brand and type
    brand, type_ = brand_type.split("_")

    # Construct folder_path
    folder_path = f"database/{brand}/{type_}"

    # List to store image paths and loaded images
    image_data = []

    # Iterate over the image IDs and construct the file paths
    for id_str in image_ids:
        # Convert the ID to an integer
        id_num = int(id_str)
        
        # Format the image file name based on the ID
        if id_num < 10:
            file_name = f'0{id_num}.png'
        else:
            file_name = f'{id_num}.png'
        
        # Construct the full file path
        file_path = os.path.join(folder_path, file_name)
        
        # Load the image using PIL
        image = Image.open(file_path)
        image_data.append((file_path, image))
    
    return image_data


def read_link_price(image_ids:list, brand_type:str ):
# Split brand_type into brand and type
    brand, type_ = brand_type.split("_")

    # Construct folder_path
    folder_path = f"database/{brand}/{brand}.xlsx"

    # Read the Excel file
    df = pd.read_excel(folder_path, sheet_name=type_)

    # Filter the DataFrame based on image IDs
    filtered_df = df[df['Item ID'].astype(str).isin(image_ids)][['Item ID','Price', 'Link']]
    
    return filtered_df


def read_input_img(image_url):
    # Request the image data from the URL
    response = requests.get(image_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Create a BytesIO object to store the image data
        image_bytes = BytesIO(response.content)
        
        # Open the image using PIL (Python Imaging Library)
        img = Image.open(image_bytes)
        
        # Save the image data in a variable (optional)
        return img