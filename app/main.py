from fastapi import FastAPI, HTTPException, status

from app.schema import (
    WorkflowCreate,
    WorkflowExeReq,
    WorkflowExeResponse,
    WorkflowResponse,
)
from app.services import create_workflow, execute_workflow, get_workflow

app = FastAPI()


@app.get("/home")
async def home():
    return {"message": "home route"}


@app.post(
    "/api/v1/workflows",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workflow_api(workflow_data: WorkflowCreate):
    workflow = create_workflow(workflow_data)
    return workflow


@app.get("/api/v1/workflows/{workflow_id}", response_model=WorkflowResponse)
def get_workflow_by_id(workflow_id: int):
    workflow = get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found"
        )
    return workflow


@app.post("/api/v1/workflows/{workflow_id}/execute", response_model=WorkflowExeResponse)
def execute_workflow_endpoint(
    workflow_id: int,
    request: WorkflowExeReq,
):
    try:
        return execute_workflow(
            workflow_id,
            request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
