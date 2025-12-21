# Sample Documents

This folder contains sample medical and insurance documents for testing the Automated Claim Processing Agent.

## Document Types

- **Medical Bills**: Hospital bills, doctor visit receipts, prescription receipts
- **Insurance Claims**: EOB (Explanation of Benefits), claim forms, insurance statements
- **Formats**: PDF, JPG, PNG

## Sample Documents Included

1. `medical_bill_sample.pdf` - Sample hospital bill (PDF format)
2. `medical_bill_sample.jpg` - Sample medical bill (JPG format)
3. `insurance_eob_sample.pdf` - Sample Explanation of Benefits (PDF format)
4. `insurance_eob_sample.png` - Sample EOB document (PNG format)
5. `insurance_claim_sample.png` - Sample insurance claim form (PNG format)
6. `prescription_receipt_sample.jpg` - Sample prescription receipt (JPG format)

All documents contain sample/test data only - no real patient information.

## Where to Get More Samples

### Public Sample Documents

1. **HIPAA Sample Documents**: 
   - Search for "HIPAA sample medical documents" (de-identified)
   - Many healthcare software vendors provide sample documents

2. **Insurance Sample Forms**:
   - Insurance company websites often have sample EOBs
   - Look for "sample explanation of benefits"

3. **Create Your Own Test Documents**:
   - Use any receipt/bill template
   - Remove or redact personal information
   - Focus on structure: dates, amounts, itemized lists

## Testing with These Samples

1. Start the backend server
2. Start the frontend
3. Navigate to http://localhost:3000
4. Upload any sample document from this folder
5. The system will extract information using PaddleOCR and ERNIE

## Note

These are sample/test documents. For production use, ensure all documents comply with privacy regulations (HIPAA, etc.).

