from pydantic import BaseModel, Field
from typing import Optional

class AgentReturnState(BaseModel):
    output: str

class AgentState(BaseModel):
    input: Optional[str] = None
    outputs: Optional[str] = ""
    inputs: list[str] = []
    remaining_input: Optional[str] = None
    query_result: Optional[str] = None
    max_itration: Optional[int] = 0
    is_fulfullied: Optional[bool] = None
    next_node: Optional[str] = None
    output: Optional[str] = None
    database: Optional[str] = None
    error: Optional[str] = None
    
    
    
class Inputrefine(BaseModel):
    inputs: list[str] = Field(
        description="""Divide the input into multiple chunks according to input
        if user requests multiple things.""")
    
class SelectDatabase(BaseModel):
    database: str = Field(
        description="Select the database that is relevant to the input and output.")
    
class SelectOutputChecker(BaseModel):
    missing_info: Optional[str] = Field(description="Description of any missing information in the response", default=None)
    fulfilled: bool = Field(description="Whether the response fully answers the user's query")
