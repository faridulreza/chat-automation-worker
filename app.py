import os
from typing import Optional, List

from fastapi import FastAPI, Body, HTTPException, status, BackgroundTasks
from fastapi.responses import Response
from executor.execute import execute
from executor.DataModel import ExecutionDataModel
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.post("/execute")
async def execute_code(body:ExecutionDataModel, background_tasks: BackgroundTasks):    
    # process in the background
    background_tasks.add_task(execute, body)
    return {"status": "Execution started", "automation_id": body.automation_id}
    
    
    
    
