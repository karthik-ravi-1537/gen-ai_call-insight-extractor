# services/call_service.py

from datetime import datetime, date
from typing import Optional
from uuid import UUID

import llm_client
from models.call import Call
from models.enums import CallStatus
from models.insight import Insight
from sqlalchemy.orm import Session


def process_transcripts_for_call(db: Session, call_id: str) -> Call:
    """
    Process all transcripts in a call by invoking the LLM for each transcript
    and then aggregating their summaries into a call-level summary.
    """
    call: Optional[Call] = db.query(Call).filter(Call.id == UUID(call_id)).first()
    if not call:
        raise Exception("Call not found")

    call.call_status = CallStatus.processing
    db.commit()

    for transcript in call.transcripts:
        if transcript.processed_at is None:
            llm_data = llm_client.process_transcript(transcript.transcript_text)

            payment_date = None
            if llm_data.get("payment_date"):
                try:
                    # Try to parse the date string into a date object
                    payment_date = date.fromisoformat(llm_data.get("payment_date"))
                except ValueError:
                    # Handle invalid date format
                    payment_date = None

            insight = Insight(
                transcript_id=transcript.id,
                payment_status=llm_data.get("payment_status"),
                payment_amount=llm_data.get("payment_amount"),
                payment_date=payment_date,
                payment_method=llm_data.get("payment_method"),
                summary_text=llm_data.get("summary_text"),
                llm_summary_updated_at=datetime.utcnow()
            )
            db.add(insight)
            transcript.processed_at = datetime.utcnow()
            db.commit()

    # Aggregate raw summaries from all transcript insights.
    raw_summaries = [
        transcript.insight.summary_text
        for transcript in call.transcripts
        if transcript.insight and transcript.insight.summary_text
    ]
    call.raw_summary = " | ".join(raw_summaries)

    # Optimization: if only one transcript, use its summary directly.
    if len(call.transcripts) == 1:
        call.processed_summary = raw_summaries[0] if raw_summaries else "No transcript insights available."
        call.call_llm_summary_updated_at = datetime.utcnow()
    else:
        if call.raw_summary:
            call.processed_summary = llm_client.process_call_summary(call.raw_summary)
            call.call_llm_summary_updated_at = datetime.utcnow()
        else:
            call.processed_summary = "No transcript insights available."

    call.call_status = CallStatus.processed
    db.commit()
    return call


def redo_call_summary(db: Session, call_id: str) -> Call:
    """
    Trigger a manual redo of the call-level summary.
    """
    call: Optional[Call] = db.query(Call).filter(Call.id == UUID(call_id)).first()
    if not call:
        raise Exception("Call not found.")

    if call.call_llm_retry_count >= 20:
        raise Exception("Maximum call redo attempts reached.")

    raw_summaries = [
        transcript.insight.summary_text
        for transcript in call.transcripts
        if transcript.insight and transcript.insight.summary_text
    ]
    if not raw_summaries:
        raise Exception("No transcript summaries available for redo.")

    call.raw_summary = " | ".join(raw_summaries)
    call.processed_summary = llm_client.process_call_summary(call.raw_summary)
    call.call_llm_summary_updated_at = datetime.utcnow()
    call.call_llm_retry_count += 1
    db.commit()
    return call
