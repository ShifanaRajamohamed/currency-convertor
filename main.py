# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Hello, FastAPI!"}


import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
# from langchain.chat_models import ChatGoogleGemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Langchain components
# llm = ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-1.5-flash")
llm = ChatGoogleGenerativeAI(
    google_api_key=api_key,
    model="gemini-2.5-flash"
)
prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""You are a currency converter agent. Your task is to provide currency information based on the user's input.
    The user will provide a country name or a currency conversion request (e.g., "convert 100 USD to EUR").
    If the user provides a country name, return the name of its currency, its current value relative to USD (if possible), and any significant differences or characteristics of that currency.
    If the user provides a conversion request, return the converted amount and the names of the currencies involved.
    Provide a concise and informative response.

    User input: {user_input}
    """
)

# Refactor LLMChain to use RunnableSequence and StrOutputParser
llm_chain = prompt | llm | StrOutputParser()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "currency_info": None})

@app.post("/convert")
async def convert_currency(request: Request, user_input: str = Form(...)):
    try:
        print(f"Received input for currency conversion: {user_input}")
        currency_info = llm_chain.invoke({"user_input": user_input})
        print(f"Currency information: {currency_info}")
        return {"response": currency_info}
    except Exception as e:
        print(f"Error in convert_currency: {e}")
        return {"response": f"Error: {e}"}
