# services/transcript_service.py

from datetime import datetime

import llm_client
from models.insight import Insight
from models.transcript import Transcript
from sqlalchemy.orm import Session


def redo_transcript_summary(db: Session, transcript_id: str) -> Insight:
    """
    Trigger a manual redo of the LLM summary for a transcript.
    This is only allowed if the user-modified summary is newer than the LLM-generated one.
    """
    transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
    if not transcript or not transcript.insight:
        raise Exception("Transcript or insight not found")

    insight = transcript.insight
    if insight.llm_retry_count >= 5:
        raise Exception("Maximum transcript redo attempts reached.")

    if insight.user_summary_updated_at and insight.user_summary_updated_at > insight.llm_summary_updated_at:
        insight.llm_redo_required = True
    else:
        raise Exception("Redo not required based on timestamps.")

    llm = llm_client
    llm_data = llm.process_transcript(transcript.transcript_text)
    insight.summary_text = llm_data.get("summary_text")
    insight.llm_summary_updated_at = datetime.utcnow()
    insight.llm_redo_required = False
    insight.llm_retry_count += 1
    db.commit()
    return insight
