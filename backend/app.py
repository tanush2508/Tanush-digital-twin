from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from time import perf_counter
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from backend.config import settings
from backend.evidence import build_evidence_packet
from backend.embed import embed_texts_async
from backend.planner import plan_query
from backend.policy import apply_policy
from backend.responder import generate_answer
from backend.retriever import retrieve_chunks_from_vector
from backend.schemas import ChatRequest, ChatResponse, DebugTrace, SourceSnippet, StatusResponse
from backend.vector_store import LocalVectorStore
from backend.verifier import verify_answer


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = LocalVectorStore()
    if store.is_ready():
        store.load()
    app.state.vector_store = store
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    store: LocalVectorStore = app.state.vector_store
    return StatusResponse(
        app_name=settings.app_name,
        index_ready=store.is_ready(),
        memory_counts=store.count_by_layer(),
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    store: LocalVectorStore = app.state.vector_store
    timings_ms: dict[str, float] = {}

    # planner + query embedding in parallel
    t0 = perf_counter()
    plan, query_vectors = await asyncio.gather(
        plan_query(payload.message),
        embed_texts_async([payload.message]),
    )
    timings_ms["plan_plus_embed"] = round((perf_counter() - t0) * 1000, 1)

    query_vector = query_vectors[0]

    t1 = perf_counter()
    results = retrieve_chunks_from_vector(
        query_vector=query_vector,
        plan=plan,
        store=store,
    )
    evidence_packet = build_evidence_packet(results)
    timings_ms["retrieve_plus_evidence"] = round((perf_counter() - t1) * 1000, 1)

    t2 = perf_counter()
    response = await generate_answer(payload.message, evidence_packet)
    timings_ms["respond"] = round((perf_counter() - t2) * 1000, 1)

    t3 = perf_counter()
    verifier_result = await verify_answer(payload.message, evidence_packet, response["answer"])
    timings_ms["verify"] = round((perf_counter() - t3) * 1000, 1)

    t4 = perf_counter()
    final = apply_policy(payload.message, response["answer"], verifier_result, plan)
    timings_ms["policy"] = round((perf_counter() - t4) * 1000, 1)

    timings_ms["total"] = round(sum(timings_ms.values()), 1)

    sources = [
        SourceSnippet(
            chunk_id=item["chunk_id"],
            source=item["source"],
            title=item["title"],
            layer=item["layer"],
            snippet=item["content"][:220],
            score=item["score"],
        )
        for item in evidence_packet
    ]

    debug = None
    if payload.debug:
        debug = DebugTrace(
            planner=plan,
            retrieved_chunks=evidence_packet,
            verifier=verifier_result,
            policy={
                "action": final["action"],
                "confidence": final["confidence"],
            },
            timings_ms=timings_ms,
        )

    return ChatResponse(
        answer=final["answer"],
        confidence=final["confidence"],
        sources=sources,
        debug=debug,
    )