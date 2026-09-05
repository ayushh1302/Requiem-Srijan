from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.storage.database import get_full_analysis
from backend.services.report_service import generate_pdf_report

router = APIRouter(tags=["Report"])

@router.get("/report/{session_id}")
async def download_report(session_id: str):
    """
    Generates and downloads the executive summary PDF report for the analyzed contract.
    """
    analysis = get_full_analysis(session_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found for this session ID. Please analyze a contract first.")

    try:
        pdf_path = generate_pdf_report(analysis)
        path_obj = Path(pdf_path)

        if not path_obj.exists():
            raise HTTPException(status_code=500, detail="Failed to generate PDF report file.")

        return FileResponse(
            path=str(path_obj),
            media_type="application/pdf",
            filename=path_obj.name,
            headers={"Content-Disposition": f'attachment; filename="{path_obj.name}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF report generation error: {str(e)}")
