# services/call_service.py

import asyncio
from datetime import datetime, timezone
from typing import List
from uuid import UUID

import llm_client
from database import get_db
from fastapi import UploadFile
from models.entities.call import Call
from models.enums import CallStatus
from repositories import call_repository
from services import transcript_service
from sqlalchemy.orm import Session


async def create_call(
        db: Session,
        files: List[UploadFile],
) -> Call:
    """Create a new call entry in the database and return it."""
    call = call_repository.create(db)

    for file in files:
        await transcript_service.create_transcript(db, call.id, file)

    return call


async def setup_and_initiate_process_call(call_id: UUID):
    """Process a call with its own session management."""
    db = next(get_db())
    try:
        call = call_repository.get_by_id(db, call_id)
        if not call:
            raise Exception(f"Call with ID {call_id} not found!")

        await process_call(db, call)
    finally:
        db.close()


async def process_call(db: Session, call: Call):
    """
    Process all transcripts in a call by invoking the LLM for each transcript
    and then aggregating their summaries into a call-level summary.
    """
    if not call:
        raise Exception("Call not found")

    call.call_status = CallStatus.PROCESSING
    call_repository.save(db, call)

    transcripts = transcript_service.get_transcripts_by_call_id(db, call.id)

    for transcript in transcripts:
        await transcript_service.process_transcript(db, transcript)

    raw_summaries = [
        transcript.insight.ai_summary
        for transcript in transcripts
        if transcript.insight and transcript.insight.ai_summary
    ]

    if not raw_summaries:
        call.raw_summary = ""
        call.ai_summary = "No transcript insights available!"
    elif len(call.transcripts) == 1:
        call.raw_summary = raw_summaries[0]
        call.ai_summary = raw_summaries[0]
    else:
        call.raw_summary = " ||| ".join(raw_summaries)
        call.ai_summary = await asyncio.to_thread(llm_client.process_call_summary, call.raw_summary)

    call.ai_summary_updated_at = datetime.now(timezone.utc)

    call.call_status = CallStatus.PROCESSED
    call_repository.save(db, call)
