# apis/transcript_api.py

from uuid import UUID

import services.transcript_service as transcript_service
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from models.insight import Insight
from sqlalchemy.orm import Session

router = APIRouter()


@router.put("/update_user_summary/{transcript_id}")
async def update_user_summary(
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
        "user_summary": insight.user_summary,
        "user_summary_updated_at": insight.user_summary_updated_at.isoformat()
    })


@router.post("/generate_refined_summary/{transcript_id}")
async def generate_refined_summary(
        transcript_id: str,
        db: Session = Depends(get_db)
):
    try:
        insight = db.query(Insight).filter(Insight.transcript_id == UUID(transcript_id)).first()
        if not insight:
            raise HTTPException(status_code=404, detail="No insight found for this transcript!")

        insight = await transcript_service.generate_refined_summary(db, str(insight.id))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={
        "message": "Refined summary generated successfully.",
        "transcript_id": str(insight.transcript_id),
        "insight_id": str(insight.id),
        "refined_summary": insight.refined_summary,
        "refined_summary_updated_at": insight.refined_summary_updated_at.isoformat(),
        "llm_refinement_count": insight.llm_refinement_count,
        "llm_refinement_required": insight.llm_refinement_required
    })
