from typing import Any

from app.schema import (
    StepExeResult,
    WorkflowCreate,
    WorkflowExeReq,
    WorkflowExeResponse,
    WorkflowResponse,
)

#in memory db
workflows:dict[int,WorkflowResponse]={}

#id counter
worlflow_id_counter=1

#workflow create
def create_workflow(
        workflow_data:WorkflowCreate
)->WorkflowResponse:
    global worlflow_id_counter  # noqa: PLW0602
    workflow_id=worlflow_id_counter

    workflow=WorkflowResponse(
        id=workflow_id,
        name=workflow_data.name,
        steps=workflow_data.steps,
        steps_count=len(workflow_data.steps)
    )

    workflows[workflow_id]=workflow

    worlflow_id_counter+=1
     
    return workflow

#get workflow by id
def get_workflow(workflow_id:int)->WorkflowResponse|None:
    return workflows.get(workflow_id)



#transfrom text
def transform_text(
        data:dict[str,Any],
        config:dict[str,Any]
)->dict[str,Any]:
    operation=config.get("operation")
    field=config.get("field")

    if field not in data:
        raise ValueError(f"Field {field} not found")

    value= data[field]

    if not isinstance (value,str):
        raise ValueError(f"Field {field} must be a string") 
    
    if operation=="uppercase":
        result=value.upper()
    elif operation=="lowercase":
        result=value.lower()
    else:
        raise ValueError(f"invalid operation")
    
    return {
        field:result
    }


def calculation(
        data:dict[str,Any],
        config:dict[str,Any]
)->dict[str,Any]:
    operation=config.get("operation")
    field=config.get("field")
    value=config.get("value")

    if field not in data:
        raise ValueError(f"Field {field} not found")
    
    current_value=data[field]

    if (isinstance(current_value,bool) or not isinstance(current_value,(int,float))):
        raise ValueError(f"Field {field} must contain a number")
    if (isinstance(value,bool) or not isinstance(value,(int,float))):
        raise ValueError("configuration value must be a number")
    if operation == "multiply":
        result=current_value*value

    elif operation=="subtract":
        result=current_value-value

    else:
        raise ValueError(f"invalid calculate operation: {operation}") 
    
    output_field= config.get(
        "output_field",
        field
    )

    return {
        output_field:result
    }
    

def excute_step(
        step,
        data:dict[str,Any],
)->dict[str,Any]:
    if step.workflow_type=="transform_text":
        return transform_text(
            data,
            step.config
        )
    elif step.workflow_type=="calculate":
        return calculation(data,step.config)
    else:
        raise ValueError(
            f"invalid step type:{step.workflow_type}"
        )


def execute_workflow(
        workflow_id:int,
        request:WorkflowExeReq
)->WorkflowExeResponse:
    workflow=get_workflow(workflow_id)
    if workflow is None:
        raise ValueError("workflow not found.")
    
    output=request.input.copy()
    steps_results:list[StepExeResult]=[]

    workflow_status="SUCCESS"
    for step in workflow.steps:
        try:
            step_output=excute_step(step,output)
            output.update(step_output)

            steps_results.append(
                StepExeResult(
                    name=step.name,
                    status="SUCCESS",
                    output=step_output
                )
            )
        except Exception as e:
            workflow_status="FAILED"
            steps_results.append(
                StepExeResult(
                    name=step.name,
                    status="FAILED",
                    output={},
                    failed=str(e)
                )
            )
            break

    return WorkflowExeResponse(
        workflow_name=workflow.name,
        status=workflow_status,
        output=output,
        step=steps_results
    )

    