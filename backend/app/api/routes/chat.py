import json
import logging
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies import get_assistant, get_session_store
from app.domain.assistant import AssistantService
from app.domain.session import SessionStore
from app.schemas.chat import QuestionRequest, AnswerResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat")
async def chat(
    body: QuestionRequest,
    assistant: AssistantService = Depends(get_assistant),
    store: SessionStore = Depends(get_session_store),
):
    session_id = body.session_id or str(uuid.uuid4())
    session = store.get_or_create(session_id)
    logger.info("POST /api/chat [%s]: %s", session_id[:8], body.question[:80])

    async def generate():
        try:
            yield f"data: {json.dumps({'type': 'session', 'session_id': session_id}, ensure_ascii=False)}\n\n"
            async for event in assistant.ask_stream(body.question, session=session):
                yield event
        except ConnectionError as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            logger.exception("Ошибка в chat stream")
            yield f"data: {json.dumps({'type': 'error', 'message': msg}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
