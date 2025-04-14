from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import docker_executor  # this must exist in your backend folder

app = FastAPI()

# In-memory "database" for function metadata
functions_db = {}

# Model for function metadata
class FunctionMetadata(BaseModel):
    name: str
    route: str
    language: str
    timeout: Optional[int] = 5  # default timeout 5 sec

# Model for execute request body
class ExecuteRequest(BaseModel):
    code: str
    language: str
    timeout: Optional[int] = 5

@app.get("/")
def root():
    return {"message": "Serverless Function Platform"}

# -------------------------------
# CRUD: Function Metadata (Task 2)
# -------------------------------

@app.post("/functions/")
def create_function(metadata: FunctionMetadata):
    func_id = str(uuid.uuid4())
    functions_db[func_id] = metadata
    return {"id": func_id, "metadata": metadata}

@app.get("/functions/")
def list_functions():
    return functions_db

@app.get("/functions/{func_id}")
def get_function(func_id: str):
    if func_id in functions_db:
        return functions_db[func_id]
    raise HTTPException(status_code=404, detail="Function not found")

@app.delete("/functions/{func_id}")
def delete_function(func_id: str):
    if func_id in functions_db:
        del functions_db[func_id]
        return {"message": "Function deleted"}
    raise HTTPException(status_code=404, detail="Function not found")

# -------------------------------
# Docker Execution Endpoint (Task 3)
# -------------------------------

@app.post("/execute")
def execute_function(req: ExecuteRequest):
    try:
        output = docker_executor.execute_function(
            code=req.code,
            language=req.language,
            timeout=req.timeout
        )
        return output if isinstance(output, dict) else {"output": output, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

