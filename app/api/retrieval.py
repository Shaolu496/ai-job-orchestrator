from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_session
from app.providers.embeddings import FakeEmbeddingProvider
from app.schemas import RetrievalRequest
from app.services.retrieval import query_chunks

router = APIRouter(prefix="/retrieval", tags=["retrieval"])
SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/query")
def query_retrieval(request: RetrievalRequest, session: SessionDep) -> dict:
    results = query_chunks(
        session,
        query=request.query,
        top_k=request.top_k,
        embedding_provider=FakeEmbeddingProvider(),
    )
    return {"results": results}
