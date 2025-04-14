from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import docker_executor

app = FastAPI()
functions_db = {}

class FunctionMetadata(BaseModel):
    name: str
    route: str
    language: str
    timeout: Optional[int] = 5
    code: Optional[str] = ""

class ExecuteRequest(BaseModel):
    code: Optional[str] = None
    language: str
    timeout: Optional[int] = 5
    runtime: Optional[str] = "runc"
    args: Optional[str] = ""

@app.post("/functions/")
def create_function(metadata: FunctionMetadata):
    func_id = str(uuid.uuid4())
    functions_db[func_id] = metadata
    return {"id": func_id, "metadata": metadata}

@app.put("/functions/{func_id}")
def update_function(func_id: str, metadata: FunctionMetadata):
    if func_id in functions_db:
        functions_db[func_id] = metadata
        return {"id": func_id, "metadata": metadata}
    raise HTTPException(status_code=404, detail="Function not found")

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

@app.post("/execute")
def execute_function(req: ExecuteRequest):
    try:
        if not req.code:
            raise HTTPException(status_code=422, detail="Code is required for ad-hoc execution")
        code = req.code
        if req.args:
            code += f"\nprint({req.args})"
        output = docker_executor.execute_function(
            code=code,
            language=req.language,
            timeout=req.timeout,
            runtime=req.runtime
        )
        return output if isinstance(output, dict) else {"output": output, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/functions/{func_id}/execute")
def execute_stored_function(func_id: str, req: ExecuteRequest):
    if func_id not in functions_db:
        raise HTTPException(status_code=404, detail="Function not found")

    meta = functions_db[func_id]
    full_code = meta.code
    if req.args:
        full_code += f"\nprint({req.args})"

    return docker_executor.execute_function(
        code=full_code,
        language=meta.language,
        timeout=meta.timeout,
        runtime=req.runtime
    )
