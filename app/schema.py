from typing import Any, Literal

from pydantic import BaseModel, Field


class WorkflowSteps(BaseModel):
    name: str = Field(min_length=2)
    workflow_type: Literal["transform_text", "calculate", "classify_text"]
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    steps: list[WorkflowSteps] = Field(min_length=1)


class WorkflowResponse(BaseModel):
    id: int
    name: str
    steps: list[WorkflowSteps]
    steps_count: int


class WorkflowExeReq(BaseModel):
    input: dict[str, Any]


class StepExeResult(BaseModel):
    name: str
    status: str
    output: dict[str, Any] = Field(default_factory=dict)
    failed: str | None = None


class WorkflowExeResponse(BaseModel):
    workflow_name: str
    status: str
    output: dict[str, Any]
    step: list[StepExeResult]


class WorkflowGenerateRequest(BaseModel):
    description: str = Field(min_length=1, max_length=1000)


class ClassificationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=3000)

    categories: list[str] = Field(
        default_factory=lambda: ["positive", "negative", "neutral"], min_length=2
    )
