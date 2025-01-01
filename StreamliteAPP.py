import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file,get_table_data
from src.mcqgenerator.mcqgenerator import generate_evaluate_chain
import streamlit as st
from src.mcqgenerator.logger import logging
#from langchain.callbacks import get_openai_callback
from langchain_community.callbacks.manager import get_openai_callback

#load json file
with open("C:\Data\GenAI Project\Response.json", 'r') as file:
    RESPONSE_JSON = json.load(file)

#create a title of app
st.title("MCQs creator Application with Langchain")

#Create a form using  st.form
with st.form("user_inputs"):
    #file upload
    uploaded_file= st.file_uploader("Upload a PDF or txt file")

    #input fields
    mcq_count=st.number_input("No. of MCQs", min_value=3,max_value=50)
    #Subject
    subject=st.text_input("Insert Subject", max_chars=20)
    #tone
    tone=st.text_input("Complexity level of questions", max_chars=20,placeholder="Simple")
    #Add Button
    button=st.form_submit_button("Create MCQs")

    #Check if button is clicked and all fields have input

    if button and uploaded_file is not None  and mcq_count and subject and tone:
        with st.spinner("Loading..."):
            try:
                text=read_file(uploaded_file)
                #count tokens and the cost of API Call
                with get_openai_callback() as cb:
                    response=generate_evaluate_chain(
                        {
                            "text": text,
                            "number": mcq_count,
                            "subject":subject,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON)
                        }
                    )
                    #st_write(response)
            
            except Exception as e:
                #traceback.print_exc(type(e), e,e.__traceback__)
                traceback.print_exc()
                st.error("Error")

            else:
                print(f"Total Tokens:{cb.total_tokens}")
                print(f"Prompt Tokens:{cb.prompt_tokens}")
                print(f"Completion Tokens:{cb.completion_tokens}")
                print(f"Total Cost:{cb.total_cost}")
                if isinstance(response, dict):
                    #extrct quiz data from response
                    quiz=response.get("quiz",None)
                    if quiz is not None:
                        table_data=get_table_data(quiz)
                        if table_data is not None:
                            df=pd.DataFrame(table_data)
                            df.index=df.index+1
                            st.table(df)
                            #display the review in a text box as well
                            st.text_area(label="Review",value=response["review"])
                        else:
                            st.error("Error in table data")
                else:
                    st.write(reponse)
