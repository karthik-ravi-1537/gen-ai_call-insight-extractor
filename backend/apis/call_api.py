# apis/call_api.py

from typing import List

from database import get_db
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from models.entities.call import Call
from services import call_service
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/upload_call")
async def upload_call(
        background_tasks: BackgroundTasks,
        files: List[UploadFile] = File(...),
        db: Session = Depends(get_db)
):
    if len(files) > 4:
        raise HTTPException(status_code=400, detail="A call can have a maximum of 4 transcripts.")

    call = await call_service.create_call(db, files)

    background_tasks.add_task(call_service.setup_and_initiate_process_call, call.id)

    return JSONResponse(content={
        "call_id": str(call.id),
        "message": "Call uploaded successfully. Processing in background."
    })


@router.get("/summaries")
def get_summaries(db: Session = Depends(get_db)):
    calls = db.query(Call).all()
    # print(f"Found {len(calls)} calls in the database")

    summaries = []
    for call in calls:
        try:
            transcripts_list = []
            for transcript in call.transcripts:
                insight_data = None
                if transcript.insight:
                    insight_data = {
                        "payment_status": transcript.insight.payment_status.value,
                        "payment_amount": str(transcript.insight.payment_amount),
                        "payment_currency": transcript.insight.payment_currency.value,
                        "payment_date": transcript.insight.payment_date.isoformat() if transcript.insight.payment_date else None,
                        "payment_method": transcript.insight.payment_method.value,
                        "comments": transcript.insight.comments,

                        "ai_summary": transcript.insight.ai_summary,
                        "user_summary": transcript.insight.user_summary,
                        "refined_summary": transcript.insight.refined_summary,

                        "llm_refinement_count": transcript.insight.llm_refinement_count,
                        "llm_refinement_required": transcript.insight.llm_refinement_required
                    }

                transcripts_list.append({
                    "transcript_id": str(transcript.id),
                    "file_name": transcript.file_name,
                    "file_content": transcript.file_content,
                    "uploaded_at": transcript.uploaded_at.isoformat(),
                    "processed_at": transcript.processed_at.isoformat() if transcript.processed_at else None,
                    "insight": insight_data
                })

            summary_data = {
                "call_id": str(call.id),
                "call_status": call.call_status.value,
                "raw_summary": call.raw_summary,
                "ai_summary": call.ai_summary,
                "ai_summary_updated_at": call.ai_summary_updated_at.isoformat() if call.ai_summary_updated_at else None,
                "llm_refinement_required": call.llm_refinement_required,
                "llm_refinement_count": call.llm_refinement_count,
                "created_at": call.created_at.isoformat() if call.created_at else None,
                "updated_at": call.updated_at.isoformat() if call.updated_at else None,
                "transcripts": transcripts_list
            }
            summaries.append(summary_data)
        except Exception as e:
            print(f"Error processing call {call.id}: {str(e)}")

    return JSONResponse(content={"summaries": summaries})
