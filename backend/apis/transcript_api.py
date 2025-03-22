# apis/transcript_api.py
from uuid import UUID

from database import SessionLocal
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from models.insight import Insight
from models.transcript import Transcript
from services import transcript_service
from sqlalchemy.orm import Session

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/transcript/{transcript_id}")
def get_transcript_detail(transcript_id: str, db: Session = Depends(get_db)):
    transcript = db.query(Transcript).filter(Transcript.id == UUID(transcript_id)).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found!")

    insight = transcript.insight
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found for this transcript!")

    return JSONResponse(content={
        "transcript": {
            "transcript_id": str(transcript.id),
            "call_id": str(transcript.call_id),
            "file_name": transcript.file_name,
            "transcript_text": transcript.transcript_text,
            "file_content": transcript.file_content,
            "created_at": transcript.created_at.isoformat(),
            "created_by": transcript.created_by,
            "updated_at": transcript.updated_at.isoformat(),
            "updated_by": transcript.updated_by,
            "uploaded_at": transcript.uploaded_at.isoformat(),
            "processed_at": transcript.processed_at.isoformat() if transcript.processed_at else None
        },
        "insight": {
            "insight_id": str(insight.id),
            "payment_status": insight.payment_status.value,
            "payment_amount": str(insight.payment_amount) if insight.payment_amount else None,
            "payment_currency": insight.payment_currency.value,
            "payment_date": insight.payment_date.isoformat() if insight.payment_date else None,
            "payment_method": insight.payment_method.value if insight.payment_method else None,
            "comments": insight.comments,
            "summary_text": insight.summary_text,
            "llm_summary_updated_at": insight.llm_summary_updated_at.isoformat(),
            "user_modified_summary": insight.user_modified_summary,
            "user_summary_updated_at": insight.user_summary_updated_at.isoformat() if insight.user_summary_updated_at else None,
            "llm_redo_required": insight.llm_redo_required,
            "llm_retry_count": insight.llm_retry_count,
            "created_at": insight.created_at.isoformat(),
            "created_by": insight.created_by,
            "updated_at": insight.updated_at.isoformat(),
            "updated_by": insight.updated_by
        }
    })


@router.put("/transcript/{transcript_id}/summary")
def update_transcript_summary(
        transcript_id: str,
        request: dict,
        db: Session = Depends(get_db)
):
    user_summary = request.get("user_summary")
    if not user_summary:
        raise HTTPException(status_code=400, detail="User summary is required")

    try:
        insight = db.query(Insight).filter(Insight.transcript_id == UUID(transcript_id)).first()
        if not insight:
            raise HTTPException(status_code=404, detail="No insight found for this transcript")

        insight = transcript_service.update_user_summary(db, str(insight.id), user_summary)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={
        "message": "User summary updated successfully.",
        "transcript_id": str(insight.transcript_id),
        "insight_id": str(insight.id),
        "user_modified_summary": insight.user_modified_summary,
        "user_summary_updated_at": insight.user_summary_updated_at.isoformat()
    })


@router.post("/redo_transcript_summary/{transcript_id}")
def redo_transcript_summary(transcript_id: str, db: Session = Depends(get_db)):
    try:
        insight = transcript_service.redo_transcript_summary(db, transcript_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={
        "message": "Transcript LLM summary updated.",
        "llm_retry_count": insight.llm_retry_count,
        "summary_text": insight.summary_text
    })
