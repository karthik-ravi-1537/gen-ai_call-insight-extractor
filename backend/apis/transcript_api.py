# apis/transcript_api.py
from database import SessionLocal
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from models.insight import Insight
from services import transcript_service
from sqlalchemy.orm import Session

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/insights/{insight_id}")
def get_insight_detail(insight_id: str, db: Session = Depends(get_db)):
    insight = db.query(Insight).filter(Insight.id == insight_id).first()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return JSONResponse(content={
        "insight_id": str(insight.id),
        "transcript_id": str(insight.transcript_id),
        "payment_status": insight.payment_status.value,
        "payment_amount": str(insight.payment_amount) if insight.payment_amount else None,
        "payment_date": insight.payment_date.isoformat() if insight.payment_date else None,
        "payment_method": insight.payment_method,
        "summary_text": insight.summary_text,
        "llm_summary_updated_at": insight.llm_summary_updated_at.isoformat(),
        "user_modified_summary": insight.user_modified_summary,
        "user_summary_updated_at": insight.user_summary_updated_at.isoformat() if insight.user_summary_updated_at else None,
        "llm_redo_required": insight.llm_redo_required,
        "llm_retry_count": insight.llm_retry_count,
        "created_at": insight.created_at.isoformat(),
        "updated_at": insight.updated_at.isoformat()
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
