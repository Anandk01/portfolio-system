import pdfplumber
import pytesseract
from PIL import Image
import io
import re
from typing import List, Dict, Any
from core.config import settings

# Configure Tesseract Path if provided (User's E: drive preference logic handled via config)
if settings.TESSERACT_CMD_PATH:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD_PATH

import csv
import os
from datetime import datetime

class PDFParserService:
    
    def __init__(self):
        # Create debug directory for raw extracts
        self.debug_dir = os.path.join(os.getcwd(), "data", "debug", "raw_extracts")
        os.makedirs(self.debug_dir, exist_ok=True)

    async def extract_holdings_from_pdf(self, file_content: bytes) -> List[Dict[str, Any]]:
        """
        Main entry point. Determines strategy (Text vs OCR) and extracts data.
        """
        holdings = []
        
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            # simple heuristic: check if first page has text
            first_page_text = pdf.pages[0].extract_text()
            
            if first_page_text and len(first_page_text.strip()) > 50:
                print("Text PDF detected.")
                holdings = self._extract_via_text(pdf)
            else:
                print("Scanned PDF detected. Attempting OCR.")
                holdings = self._extract_via_ocr(pdf)
        
        # SAVE TO CSV FOR AUDITABILITY
        if holdings:
            csv_path = self._save_to_csv(holdings)
            print(f"AUDIT LOG: Raw extraction saved to {csv_path}")
                
        return holdings

    def _save_to_csv(self, holdings: List[Dict[str, Any]]) -> str:
        """Saves extracted data to a CSV for debugging/transparency."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"extract_{timestamp}.csv"
        filepath = os.path.join(self.debug_dir, filename)
        
        if not holdings: return filepath
        
        keys = holdings[0].keys()
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(holdings)
            
        return filepath

    def _extract_via_text(self, pdf) -> List[Dict[str, Any]]:
        extracted_data = []
        
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                parsed_rows = self._parse_table(table)
                extracted_data.extend(parsed_rows)
                
        return extracted_data

    def _extract_via_ocr(self, pdf) -> List[Dict[str, Any]]:
        """
        Fallback for scanned PDFs. Converts pages to images and uses Tesseract.
        """
        extracted_data = []
        try:
            for page in pdf.pages:
                # Convert PDF page to image
                # Note: pdfplumber has .to_image() which requires Wand or similar, 
                # but standard approach often uses 'pdf2image'. 
                # For this snippet, assuming pdfplumber's image extraction or basic text fallback.
                # Since 'pdf2image' requires poppler which is a heavy external dep, 
                # we will try to use pdfplumber's native image handling if possible or warn.
                
                # IMPORTANT: In a real scenario, we'd use 'pdf2image' here. 
                # For this prototype, we'll try to extract text from the page image object if available
                # Or just return empty and warn the user they need a text-based PDF for this version 
                # unless they have the heavy image pipelines set up.
                
                # Simplified OCR stub for this environment:
                # We simply try to text-extract again with OCR enabled logic if we had the image tools.
                print("WARNING: OCR is not fully implemented in this prototype environment. Scanned PDFs may fail to extract data.")
                pass
        except Exception as e:
            print(f"OCR Failed: {e}")
            
        return extracted_data

    def _parse_table(self, table: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Normalize table rows into structured dicts.
        Heuristics: Look for columns like 'Script', 'Security', 'Unit', 'Qty', 'Buy', 'Invested'.
        """
        headers = []
        data_rows = []
        
        # 1. Identify Header Row
        header_idx = -1
        keywords = ['script', 'security', 'symbol', 'fund name', 'description', 'isin', 'instruments', 'folio']
        for i, row in enumerate(table):
            # clean None values
            row_text = [str(c).lower() if c else "" for c in row]
            # Check for common header keywords using substring match
            if any(k in cell for cell in row_text for k in keywords):
                headers = row_text
                header_idx = i
                break
        
        if header_idx == -1:
            if table and len(table) > 0:
                print(f"WARNING: No header row found in table. First row: {table[0]}")
            return []
        
        print(f"DEBUG: Found headers at row {header_idx}: {headers}")

        col_map = {}
        for idx, col_name in enumerate(headers):
            # 1. Name/Security identification
            if any(k in col_name for k in ['script', 'security', 'fund', 'symbol', 'description', 'company']):
                col_map['name'] = idx
            
            # 2. ISIN identification (can be same column as name)
            if 'isin' in col_name:
                col_map['isin'] = idx

            # 3. Units/Quantity (prioritize 'bal' or 'units' specifically for MFs)
            if any(k in col_name for k in ['no. of', 'qty', 'unit', 'quantity', 'bal', 'balance', 'shares']):
                # If we already have a units col, but this one says "shares" or "units" explicitly, prefer it
                if 'units' not in col_map or 'units' in col_name or 'shares' in col_name:
                    col_map['units'] = idx

            # 4. Values (Invested or Current)
            if any(k in col_name for k in ['value', 'market', 'amt', 'invested', 'price', 'cost']):
                if 'invested' in col_name or 'cost' in col_name:
                    col_map['invested'] = idx
                elif 'current' in col_name or 'market' in col_name or ('value' in col_name and 'invested' not in col_name):
                    col_map['current'] = idx
        
        print(f"DEBUG: Column mapping: {col_map}")
                    
        # 3. Extract Data
        valid_rows = []
        for i in range(header_idx + 1, len(table)):
            row = table[i]
            if not row or all(c is None for c in row): continue
            
            try:
                name_idx = col_map.get('name')
                units_idx = col_map.get('units')
                inv_idx = col_map.get('invested')
                curr_idx = col_map.get('current')
                isin_idx = col_map.get('isin')

                if name_idx is not None and row[name_idx]:
                    # Normalize whitespace and newlines completely
                    asset_name = re.sub(r'\s+', ' ', str(row[name_idx])).strip()
                    
                    # skip header repetitions or junk
                    blacklist = [
                        'script', 'total', 'page', 'description', 'security', 
                        'demat', 'account', 'folio', 'pan:', 'statement', 
                        'summary', 'report', 'as on', 'account type', 'cdsl', 'nsdl'
                    ]
                    if any(b in asset_name.lower() for b in blacklist): continue 
                    
                    units = self._parse_float(row[units_idx]) if units_idx is not None else 0.0
                    inv_val = self._parse_float(row[inv_idx]) if inv_idx is not None else 0.0
                    if curr_idx is not None and inv_val == 0.0:
                        inv_val = self._parse_float(row[curr_idx]) # Fallback to current if invested is 0
                    
                    # FILTER: If both units and value are 0, it's definitely junk/metadata
                    if units == 0.0 and inv_val == 0.0:
                        continue

                    # ISIN Extraction (try from isin_idx or from name if combined)
                    # Using a more lenient 12-char pattern [A-Z]{2}[A-Z0-9]{10}
                    isin_pattern = r'[A-Z]{2}[A-Z0-9]{10}'
                    isin = None
                    if isin_idx is not None and row[isin_idx]:
                        isin_str = str(row[isin_idx]).upper()
                        match = re.search(isin_pattern, isin_str)
                        if match:
                            isin = match.group(0)
                    
                    # Fallback to extracting from name if not found in isin column
                    if not isin:
                        match = re.search(isin_pattern, asset_name.upper())
                        if match:
                            isin = match.group(0)
                    
                    print(f"DEBUG: Extracted row - Name: {asset_name}, ISIN: {isin}, Units: {units}, Value: {inv_val}")
                    
                    valid_rows.append({
                        "raw_name": asset_name,
                        "isin": isin,
                        "quantity": units,
                        "invested_value": inv_val
                    })
            except Exception as e:
                print(f"Row parse error: {e}")
                continue
                
        return valid_rows

    def _parse_float(self, value: Any) -> float:
        if not value: return 0.0
        # Remove currency symbols, commas
        # Remove common currency identifiers
        clean = str(value).replace(',', '').replace('Rs.', '').replace('Rs', '').strip()
        # Remove any remaining non-numeric characters except decimal
        clean = re.sub(r'[^\d.]', '', clean)
        try:
            return round(float(clean), 4)
        except:
            return 0.0

pdf_service = PDFParserService()

