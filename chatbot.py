import gradio as gr
import openai
from dotenv import load_dotenv
import os
import json

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE") 
openai.api_type = 'azure'
openai.api_version = '2023-07-01-preview'

GPT_MODEL = "gpt-35-16k"
EMBEDDING_MODEL = "text-embedding-ada-002"

messages = []
 

def add_text(history, text):
    global messages  #message[list] is defined globally
    history = history + [(text,'')]
    messages = messages + [{"role":'user', 'content': text}]
    return history, ""

def generate_response(history, model ):
        global messages, cost

        response = openai.ChatCompletion.create(
            engine = GPT_MODEL,
            messages=messages,
            temperature=0.2,
            stream=True
        )

        response_msg = ""
        for chunk in response:
            if chunk["choices"][0]["finish_reason"]:
                  break
            try:
                response_msg = response_msg + chunk["choices"][0]["delta"]["content"]
                history[-1][1] = response_msg
                yield history
            except:
                 pass
             
        # cost = cost + (response.usage['total_tokens'])*(0.002/1000)
        messages = messages + [{"role":'assistant', 'content': response_msg}]

with gr.Blocks() as demo:
    
    radio = gr.Radio(value='gpt-35-16k', choices=['gpt-35-16k','gpt35'], label='models')
    chatbot = gr.Chatbot(value=[], elem_id="chatbot", height=700)
    with gr.Row():
        with gr.Column(scale=1):
            txt = gr.Textbox(
                show_label=False,
                placeholder="Enter text and press enter",
            container=False)
        # with gr.Column(scale=0.10):
        #     cost_view = gr.Textbox(label='usage in $',value=0)

    txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
            generate_response, inputs =[chatbot, radio],outputs = chatbot,)
            
demo.queue()