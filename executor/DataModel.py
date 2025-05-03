
from pydantic import ConfigDict, BaseModel
class ExecutionDataModel(BaseModel):
    automation_id: str
    start_block_id: str
    initial_state: dict
    