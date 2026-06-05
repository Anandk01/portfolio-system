from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import io
import logging
import pdfplumber
from io import BytesIO
from .service import PDFParserService
from modules.auth.router import get_current_user
from core.database import get_engine
from core.models import ParsedPortfolio
from modules.pdf_parser.format_detector import CASFormatDetector

router = APIRouter()
pdf_service = PDFParserService()
logger = logging.getLogger(__name__)

@router.post("/extract")
async def extract_holdings(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    """
    Parse PDF and save to temporary ParsedPortfolio collection.
    Returns parsed holdings with confidence score for user review.
    """
    logger.info(f"Received file upload request for: {file.filename}")
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail=f"Only PDF files allowed. Received: {file.filename}")
    
    try:
        content = await file.read()
        
        # Extract full text for format detection
        with pdfplumber.open(BytesIO(content)) as pdf:
            full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        
        # Detect CAS format
        format_type, format_confidence = CASFormatDetector.detect_format(full_text)
        logger.info(f"Detected format: {format_type} (confidence: {format_confidence})")
        
        # Extract CAS total from header
        cas_total = CASFormatDetector.extract_cas_total(full_text, format_type)
        logger.info(f"CAS total from header: ₹{cas_total}")
        
        # Parse holdings
        holdings = await pdf_service.extract_holdings_from_pdf(content)
        
        if not holdings:
            raise HTTPException(status_code=400, detail="No holdings found in PDF")
        
        # Calculate extracted total
        extracted_total = sum(h.get("invested_value", 0) for h in holdings)
        logger.info(f"Extracted total: ₹{extracted_total}")
        
        # Calculate parsing confidence
        confidence = CASFormatDetector.calculate_confidence(cas_total, extracted_total)
        logger.info(f"Parsing confidence: {confidence}")
        
        # Save to ParsedPortfolio collection
        engine = get_engine()
        
        # Delete any existing parsed portfolio for this user
        existing = await engine.find_one(ParsedPortfolio, ParsedPortfolio.user_id == current_user.id)
        if existing:
            await engine.delete(existing)
        
        # Create new parsed portfolio
        parsed_portfolio = ParsedPortfolio(
            user_id=current_user.id,
            holdings=[],  # Will be populated after normalization
            cas_total=cas_total,
            extracted_total=extracted_total,
            confidence=confidence,
            format_type=format_type,
            status="parsed"
        )
        await engine.save(parsed_portfolio)
        
        return {
            "status": "parsed",
            "holdings": holdings,
            "cas_total": cas_total,
            "extracted_total": extracted_total,
            "confidence": confidence,
            "format_type": format_type,
            "count": len(holdings)
        }
        
    except Exception as e:
        logger.error(f"PDF extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")
