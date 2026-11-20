from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_assistant
from app.domain.assistant import AssistantService
from app.schemas.chat import QuestionRequest, AnswerResponse

router = APIRouter()


@router.post("/chat", response_model=AnswerResponse)
async def chat(
    body: QuestionRequest,
    assistant: AssistantService = Depends(get_assistant),
):
    try:
        answer = await assistant.ask(body.question)
        if not answer:
            return AnswerResponse(answer="Не удалось получить ответ. Попробуйте переформулировать вопрос.")
        return AnswerResponse(answer=answer)
    except ConnectionError as e:
        raise HTTPException(503, f"LLM сервис недоступен: {e}")
    except Exception as e:
        raise HTTPException(500, f"Ошибка обработки: {type(e).__name__}: {e}")
