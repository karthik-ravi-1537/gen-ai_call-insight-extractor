# services/call_service.py

import asyncio
from datetime import datetime, date, timezone
from uuid import UUID

import llm_client
from models.call import Call
from models.enums import CallStatus, PaymentStatus, PaymentCurrency, PaymentMethod
from models.insight import Insight
from sqlalchemy.orm import Session


async def process_call(db: Session, call_id: str) -> Call:
    """
    Process all transcripts in a call by invoking the LLM for each transcript
    and then aggregating their summaries into a call-level summary.
    """
    call = db.query(Call).filter(Call.id == UUID(call_id)).first()
    if not call:
        raise Exception("Call not found")

    call.call_status = CallStatus.PROCESSING
    db.commit()

    for transcript in call.transcripts:
        if transcript.processed_at is None:
            llm_data = await asyncio.to_thread(llm_client.process_transcript, transcript.transcript_text)

            payment_date = None
            if llm_data.get("payment_date"):
                try:
                    payment_date = date.fromisoformat(llm_data.get("payment_date"))
                except ValueError:
                    payment_date = None

            comments = llm_data.get("comments")

            if llm_data.get("payment_method") and "Other - " in llm_data.get("payment_method"):
                llm_data["payment_method"] = "Other"
                comments = f"{comments}\nSpecific Payment Method: {llm_data.get('payment_method').split('Other - ')[1]}" \
                    if comments \
                    else f"Specific Payment Method: {llm_data.get('payment_method').split('Other - ')[1]}"

            if llm_data.get("payment_currency") and "Other - " in llm_data.get("payment_currency"):
                llm_data["payment_currency"] = "Other"
                comments = f"{comments}\nSpecific Payment Currency: {llm_data.get('payment_currency').split('Other - ')[1]}" \
                    if comments \
                    else f"Specific Payment Currency: {llm_data.get('payment_currency').split('Other - ')[1]}"

            payment_status = getattr(PaymentStatus, llm_data.get("payment_status", "Pending"), PaymentStatus.PENDING)
            payment_currency = getattr(PaymentCurrency, llm_data.get("payment_currency", "USD"), PaymentCurrency.USD)
            payment_method = getattr(PaymentMethod, llm_data.get("payment_method", "Cash"), PaymentMethod.CASH)

            current_time = datetime.now(timezone.utc)
            ai_summary = llm_data.get("ai_summary", "")

            history_entry = {
                "timestamp": current_time.isoformat(),
                "ai_summary": ai_summary,
                "user_summary": "",
                "refined_summary": "",
            }

            summary_history = [history_entry]

            insight = Insight(
                transcript_id=transcript.id,
                payment_status=payment_status,
                payment_amount=llm_data.get("payment_amount"),
                payment_currency=payment_currency,
                payment_date=payment_date,
                payment_method=payment_method,
                ai_summary=ai_summary,
                ai_summary_updated_at=current_time,
                comments=comments,
                summary_history=summary_history,
            )
            db.add(insight)
            transcript.processed_at = current_time
            db.commit()

    raw_summaries = [
        transcript.insight.ai_summary
        for transcript in call.transcripts
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
    db.commit()
    return call

# async def redo_call_summary(db: Session, call_id: str) -> Call:
#     """
#     Trigger a manual redo of the call-level summary.
#     """
#     call = db.query(Call).filter(Call.id == UUID(call_id)).first()
#     if not call:
#         raise Exception("Call not found.")
#
#     if call.call_llm_retry_count >= 20:
#         raise Exception("Maximum call redo attempts reached.")
#
#     raw_summaries = [
#         transcript.insight.ai_summary
#         for transcript in call.transcripts
#         if transcript.insight and transcript.insight.ai_summary
#     ]
#     if not raw_summaries:
#         raise Exception("No transcript summaries available for redo.")
#
#     call.raw_summary = " | ".join(raw_summaries)
#     call.ai_summary = await asyncio.to_thread(llm_client.process_call_summary, call.raw_summary)
#     call.call_llm_summary_updated_at = datetime.now(timezone.utc)
#     call.call_llm_retry_count += 1
#     db.commit()
#     return call
