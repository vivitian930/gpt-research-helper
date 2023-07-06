import gradio as gr
import openai
from dotenv import load_dotenv
import os
import json

from utils import Conversation, chat_completion_with_function_execution, arxiv_functions

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE") 
openai.api_type = 'azure'
openai.api_version = '2023-07-01-preview'

GPT_MODEL = "gpt-35-16k"
EMBEDDING_MODEL = "text-embedding-ada-002"

# Start with a system message
paper_system_message = """You are arXivGPT, a helpful assistant pulls academic papers to answer user questions.
You summarize the papers clearly so the customer can decide which to read to answer their question.
You always provide the article_url and title so the user can understand the name of the paper and click through to access it.
Begin!"""
paper_conversation = Conversation()
paper_conversation.add_message("system", paper_system_message)

 

def add_text(history, text):
    global paper_conversation  #message[list] is defined globally
    history = history + [(text,'')]
    # messages = messages + [{"role":'user', 'content': text}]
    paper_conversation.add_message('user', text)
    return history, ""

def generate_response(history, model ):
        global paper_conversation

        chat_response = chat_completion_with_function_execution(
    paper_conversation.conversation_history, functions=arxiv_functions
)
        print(chat_response)
        assistant_message = chat_response["choices"][0]["message"]["content"]
        paper_conversation.add_message("assistant", assistant_message)
        print(assistant_message)
             
        # cost = cost + (response.usage['total_tokens'])*(0.002/1000)
        history[-1][1] = assistant_message
        return history

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