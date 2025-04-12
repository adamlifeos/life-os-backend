from pydantic import BaseModel

class AICoachRequest(BaseModel):
    user_input: str

class AICoachResponse(BaseModel):
    response: str
