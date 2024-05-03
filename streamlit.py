import streamlit as st
from io import StringIO
from tensorflow.keras.applications import ResNet50
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
from code.database_query import query_cloth, read_image, read_link_price
from code.langchain_clothes_alt import generate_cloth, store_img

# "with" notation
with st.sidebar:
    st.write("Input:")
    # Select cloth type
    ctype = st.selectbox(
        'What type of the clothes you looking for?',
        ('top','bottom'))

    # Select budgets
    budget = st.selectbox(
        'What is your budget?',
        ("$10-$50","$60-$150",'More than $200'))

    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type=['png', 'jpg', 'jpeg'])

# Outside of the sidebar
if uploaded_file is not None:
    # Read the uploaded file as an image
    selfie = Image.open(uploaded_file)
    
    # Display the uploaded image
    st.image(selfie, caption='Uploaded Image', use_column_width=True,)

    # Save the uploaded image to a file
    selfie.save("input_img/img.jpg") 
    
    # Generate cloth using the uploaded image
    image_url,brand_type = generate_cloth('input_img/img.jpg', budget, ctype)

    # Print image_url and brand_type in Streamlit
    # st.write(f"Image URL: {image_url}")
    st.write(f"Brand Type: {brand_type}")

    # Load the pre-trained ResNet50 model without the top classification layers
    model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

    # store the saving image_url into the input_img folder and find the match images in database
    store_img(image_url)
    image_ids = query_cloth('input_img/img.jpg', brand_type, model)
    image_data = read_image(image_ids, brand_type)


    # Display the images in a horizontal layout
    #for idx, (file_path, image) in enumerate(image_data):
        #image = Image.open(file_path)
        #st.image(image, caption=f'ID: {image_ids[idx]}')
    
    columns = st.columns(len(image_data))
    for idx, (file_path, image) in enumerate(image_data):
         with columns[idx]:
             image = Image.open(file_path)
             st.image(image, caption=f'ID: {image_ids[idx]}')

    # Set display option to show full link without truncation
    st.set_option('deprecation.showfileUploaderEncoding', False)
    df = read_link_price(image_ids, brand_type)
    # Display the DataFrame as a table
    # Display the DataFrame as a table with clickable hyperlinks
    st.dataframe(
        df,
        column_config={
            "Price": st.column_config.NumberColumn(
                format="$ %d",
        ),
            "Link": st.column_config.LinkColumn("Clothes URL"),
        },
          hide_index =True)

# streamlit run streamlit.py