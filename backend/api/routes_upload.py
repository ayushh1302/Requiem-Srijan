import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.models.schemas import DocumentUploadResponse
from backend.services.document_service import validate_and_extract, DocumentParsingError
from backend.storage.database import save_session, save_raw_contract
from backend.services.scoring_service import detect_contract_type

router = APIRouter(tags=["Upload"])

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(None)
):
    """
    Validates uploaded file, extracts text, and initializes session.
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    try:
        file_bytes = await file.read()
        filename = file.filename or "uploaded_contract.pdf"

        text, file_type, page_count, char_count = validate_and_extract(filename, file_bytes)

        # Detect likely contract type
        contract_type = detect_contract_type(text, filename)

        # Save session & raw contract to SQLite
        save_session(session_id, filename, file_type, contract_type)
        save_raw_contract(session_id, filename, text, page_count, char_count)

        words = len(text.split())

        return DocumentUploadResponse(
            session_id=session_id,
            filename=filename,
            file_type=file_type,
            page_count=page_count,
            text_length=words,
            char_count=char_count,
            message=f"Successfully extracted {words} words from {filename}."
        )
    except DocumentParsingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error processing document: {str(e)}")
