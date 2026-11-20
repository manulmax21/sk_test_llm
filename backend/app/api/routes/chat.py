import json
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies import get_assistant
from app.domain.assistant import AssistantService
from app.schemas.chat import QuestionRequest, AnswerResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat")
async def chat(
    body: QuestionRequest,
    assistant: AssistantService = Depends(get_assistant),
):
    logger.info("POST /api/chat: %s", body.question[:80])

    async def generate():
        try:
            async for event in assistant.ask_stream(body.question):
                yield event
        except ConnectionError as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            logger.exception("Ошибка в chat stream")
            yield f"data: {json.dumps({'type': 'error', 'message': msg}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
