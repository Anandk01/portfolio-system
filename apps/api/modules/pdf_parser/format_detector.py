"""
CAS Format Detection Module
Detects the format of uploaded Consolidated Account Statements
and routes to appropriate parser strategy.
"""

import re
from typing import Tuple

class CASFormatDetector:
    """Detects CAS format from text patterns"""
    
    @staticmethod
    def detect_format(text: str) -> Tuple[str, float]:
        """
        Detect CAS format and return format type with confidence score.
        
        Returns:
            Tuple[str, float]: (format_type, confidence)
            format_type: "NSDL", "CDSL", "CAMS", "KFINTECH", "UNKNOWN"
            confidence: 0.0 to 1.0
        """
        text_upper = text.upper()
        
        # NSDL Detection
        nsdl_patterns = [
            "NATIONAL SECURITIES DEPOSITORY LIMITED",
            "NSDL CONSOLIDATED ACCOUNT STATEMENT",
            "NSDL CAS",
            "NSDL ID:"
        ]
        nsdl_matches = sum(1 for pattern in nsdl_patterns if pattern in text_upper)
        if nsdl_matches >= 2:
            confidence = min(0.9 + (nsdl_matches * 0.025), 1.0)
            return ("NSDL", confidence)
        
        # CDSL Detection
        cdsl_patterns = [
            "CENTRAL DEPOSITORY SERVICES",
            "CDSL",
            "DEPOSITORY PARTICIPANT",
            "DP ID:"
        ]
        cdsl_matches = sum(1 for pattern in cdsl_patterns if pattern in text_upper)
        if cdsl_matches >= 2:
            confidence = min(0.85 + (cdsl_matches * 0.025), 1.0)
            return ("CDSL", confidence)
        
        # CAMS Detection
        cams_patterns = [
            "COMPUTER AGE MANAGEMENT SERVICES",
            "CAMS",
            "STATEMENT OF ACCOUNT"
        ]
        cams_matches = sum(1 for pattern in cams_patterns if pattern in text_upper)
        if cams_matches >= 2:
            confidence = min(0.85 + (cams_matches * 0.025), 1.0)
            return ("CAMS", confidence)
        
        # KFintech Detection
        kfintech_patterns = [
            "KFINTECH",
            "KARVY",
            "STATEMENT OF ACCOUNT"
        ]
        kfintech_matches = sum(1 for pattern in kfintech_patterns if pattern in text_upper)
        if kfintech_matches >= 2:
            confidence = min(0.85 + (kfintech_matches * 0.025), 1.0)
            return ("KFINTECH", confidence)
        
        return ("UNKNOWN", 0.0)
    
    @staticmethod
    def extract_cas_total(text: str, format_type: str) -> float:
        """
        Extract the total portfolio value from CAS header.
        
        Args:
            text: Raw CAS text
            format_type: Detected format type
            
        Returns:
            float: Total portfolio value from CAS, or 0.0 if not found
        """
        try:
            if format_type == "NSDL":
                # Look for "YOUR CONSOLIDATED PORTFOLIO VALUE" followed by amount
                # Pattern: ` 45,690.09 or ₹ 45,690.09
                pattern = r'(?:YOUR CONSOLIDATED PORTFOLIO VALUE|TOTAL)[\s\S]{0,100}?[`₹]\s*([\d,]+\.?\d*)'
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    return float(amount_str)
            
            elif format_type == "CDSL":
                # CDSL typically shows total at bottom
                pattern = r'(?:TOTAL|GRAND TOTAL)[\s\S]{0,50}?[`₹]\s*([\d,]+\.?\d*)'
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    return float(amount_str)
            
            # Generic fallback
            pattern = r'(?:TOTAL|PORTFOLIO VALUE)[\s\S]{0,100}?[`₹]\s*([\d,]+\.?\d*)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                return float(amount_str)
                
        except Exception as e:
            print(f"Error extracting CAS total: {e}")
        
        return 0.0
    
    @staticmethod
    def calculate_confidence(cas_total: float, extracted_total: float) -> float:
        """
        Calculate parsing confidence based on CAS total vs extracted total.
        
        Args:
            cas_total: Total from CAS header
            extracted_total: Sum of extracted holdings
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        if cas_total == 0.0 or extracted_total == 0.0:
            return 0.0
        
        difference = abs(cas_total - extracted_total)
        relative_error = difference / cas_total
        
        # Confidence decreases as error increases
        # 0% error = 1.0 confidence
        # 1% error = 0.99 confidence
        # 5% error = 0.95 confidence
        # 10% error = 0.90 confidence
        confidence = max(0.0, 1.0 - relative_error)
        
        return round(confidence, 4)
