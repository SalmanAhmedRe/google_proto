"""
IMPORTS
"""
from fastapi import FastAPI
import uvicorn
import numpy as np
from fastapi.responses import FileResponse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
import typing
import time
os.environ["OPENAI_API_KEY"] = "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"
from chat_demo import DemoGoogle
from code_executor import CodeExecutionStatus
from config import Config


"""
GLOBAL VARIABLES
"""

config = Config()
agent = DemoGoogle(csv_path = config.csv_path, images_folder=config.image_folder, plot_words_dict=config.plot_words_dict)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# """
# API CHAT
# """

# class ChatSchema(BaseModel):
#     question :str = Field(None, title="Question", max_length=1000)

# def chat_agent(x):
#     output = agent.chat(x.question)
#     filtered_output = {}
#     for each in config.default_output_keys:
#         filtered_output[each] = output[each]
#     return filtered_output

# @app.post('/api/chat_demo/')
# async def chat_demo_api(chat_schema: ChatSchema):
#     try:
#         output = chat_agent(chat_schema)
#     except:
#         output = {}
#     return output


"""
API EXPLORE
"""

class ChatSchemaExplore(BaseModel):
    idx :typing.List[int] = []
    
def chat_explore(x):
    print (x.idx)
    print (x)
    
    insights = np.array(config.explore["insights"])
    file_names = np.array(config.explore["file_names"])
    
    max_insights = len(insights)
    
    max_ = config.max_
    idx = x.idx
    idx = idx[0:max_]
    idx_ = []
    for i in idx:
        idx_.append(i % max_insights)
    
    return {
        "insights_explore" : insights[idx_].tolist(),
        "file_names_explore" : file_names[idx_].tolist(),
    }
        
@app.post('/api/chat_explore/')
async def chat_demo_api(chat_schema: ChatSchemaExplore):
    try:
        return chat_explore(chat_schema)
    except:
        return {}


"""
API CHAT STAGE 1
"""

class ChatSchemaStage1(BaseModel):
    question :str = Field(None, title="Question", max_length=1000)
    personalize_text :str = Field(None, title="Personalize Text", max_length=1000)
    is_personalize :bool
    
def chat_agent_1(x):
    output = agent.chat_stage_1(x.question)
    filtered_output = {}
    for each in config.default_output_keys:
        if each in output.keys():
            filtered_output[each] = output[each]
    return filtered_output

@app.post('/api/chat_demo_stage_1/')
async def chat_demo_api(chat_schema: ChatSchemaStage1):
    print ("Request Received 1")
    st = time.time()
    agent.ConfigPrompt.update_summary_personal_instructions(chat_schema.is_personalize, chat_schema.personalize_text)
    try:
        output = chat_agent_1(chat_schema)
        if output["filename"]:
            time.sleep(2)
    except:
        output = {}
    total_time = time.time() - st
    question = chat_schema.question
    content = f"{question}   {total_time} seconds\n"
    with open(f"log_stage_1.txt", 'a') as f:
        f.write(content)
    return output


"""
API CHAT STAGE 2
"""
class ChatSchemaStage2(BaseModel):
    insight :str = Field(None, title="Insight", max_length=1000)
    isInsight :bool
    
def chat_agent_2(x):
    x = {
        "insight" : x.insight,
        "isInsight" : x.isInsight,
        }
    output = agent.chat_stage_2(x)
    filtered_output = {}
    for each in config.default_output_keys:
        if each in output.keys():
            filtered_output[each] = output[each]
    return filtered_output

@app.post('/api/chat_demo_stage_2/')
async def chat_demo_api(chat_schema: ChatSchemaStage2):
    print ("Request Received 2")
    st = time.time()
    # agent.ConfigPrompt.update_summary_personal_instructions(chat_schema.is_personalize, chat_schema.personalize_text)
    try:
        output = chat_agent_2(chat_schema)
        if output["insight_plot_filename"]:
            time.sleep(2)
    except:
        output = {}
        
    total_time = time.time() - st
    question = chat_schema.insight
    content = f"{question}   {total_time} seconds\n"
    with open(f"log_stage_2.txt", 'a') as f:
        f.write(content)
    return output


"""
API CHAT
"""

class ChatSchema(BaseModel):
    question :str = Field(None, title="Question", max_length=1000)
    personalize_text :str = Field(None, title="Personalize Text", max_length=1000)
    is_personalize :bool
    

def chat_agent(x):
    output = agent.chat(x.question)
    filtered_output = {}
    for each in config.default_output_keys:
        filtered_output[each] = output[each]
    return filtered_output

@app.post('/api/chat_demo/')
async def chat_demo_api(chat_schema: ChatSchema):
    st = time.time()
    agent.ConfigPrompt.update_summary_personal_instructions(chat_schema.is_personalize, chat_schema.personalize_text)
    try:
        output = chat_agent(chat_schema)
        time.sleep(3)
    except:
        output = {}
    total_time = time.time() - st
    question = chat_schema.question
    content = f"{question}   {total_time} seconds\n"
    with open(f"log_full.txt", 'a') as f:
        f.write(content)
    return output



"""
PYTHON TO SQL CHAT
"""

class CodeConvertSchema(BaseModel):
    python_code :str = Field(None, title="Python Code", max_length=5000)

def covert_code(x):
    output = agent.python_to_sql(x.python_code)
    return {"sql_code" : output}

@app.post('/api/python_to_sql/')
async def python_to_sql(convert_schema: CodeConvertSchema):
    try:
        output = covert_code(convert_schema)
    except:
        output = {}
    return output


"""
PYTHON EXPLAIN CHAT
"""

class ExplainSchema(BaseModel):
    python_code :str = Field(None, title="Python Code", max_length=5000)

def explain_code(x):
    output = agent.python_explain(x.python_code)
    return {"explaination" : output}

@app.post('/api/explain_python_code/')
async def python_to_sql(explain_schema: ExplainSchema):
    try:
        output = explain_code(explain_schema)
    except:
        output = {}
    return output





"""
API INDEX
"""    

@app.get("/")
def index():
    return {"message": "AlgoMarketing Demo Welcome."}

"""
RUN API
"""

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)





























# ############################## (In case if we need to download file using FAST API)
# class FileNameSchema(BaseModel):
#     filename :str = Field(None, title="Filename", max_length=100)
#     insight_plot_filename :str = Field(None, title="Insight Filename", max_length=100)

# def download_path(x):
#     print (x.filename, x.insight_plot_filename)
#     output = None
#     if x.filename:
#         output = x.filename
#     if x.insight_plot_filename:
#         output = x.insight_plot_filename
#     return output

# @app.post("/file_download/")
# async def file_download(filename_schema: FileNameSchema):
#     try:
#         image_path = download_path(filename_schema)
#         if image_path:
#             return FileResponse(image_path)
#         return {}
#     except:
#         return {}

# ##############################
