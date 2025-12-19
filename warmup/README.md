# Warm-up Task: PDF to Web Page Generator

This is the warm-up task for the ERNIE AI Developer Challenge.

## Overview

A web page that:
1. Accepts PDF/image uploads of receipts/invoices
2. Uses PaddleOCR-VL to extract text and layout
3. Converts content to Markdown
4. Uses ERNIE to generate a web page
5. Displays results in a clean interface

## Usage

1. Open `index.html` in a web browser
2. Upload a PDF or image file (receipt/invoice)
3. The system will:
   - Extract text using PaddleOCR
   - Process with ERNIE to extract expense information
   - Generate Markdown content
   - Display the generated web page

## API Configuration

Update the `API_URL` constant in `index.html` to point to your backend:

```javascript
const API_URL = 'http://localhost:8000'; // Change to your backend URL
```

## Deployment to GitHub Pages

1. Push this repository to GitHub
2. Go to repository Settings > Pages
3. Set source to the `warmup` directory
4. Access your page at `https://yourusername.github.io/repository-name/`

## Features

- Drag & drop file upload
- Real-time processing status
- Extracted expense information display
- Markdown content generation
- Web page preview
- Error handling

## Requirements

- Backend API running (see main README for setup)
- Modern web browser with JavaScript enabled

