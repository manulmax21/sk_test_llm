from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str = Field(default="", max_length=64)


class AnswerResponse(BaseModel):
    answer: str
    logs: list[str] = []
