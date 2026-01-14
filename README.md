# Excel to DOCX Converter

> A modern, browser-based tool for converting Excel spreadsheets into formatted Word documents with intelligent column selection and data range configuration.

---

## Introduction

**Excel to DOCX Converter** is a lightweight, production-ready web application that transforms Excel data into professionally formatted Word documents. Built with Flask and modern web technologies, it provides an intuitive interface for selecting specific columns, defining data ranges, and generating custom reports from spreadsheet data.

---
## Technical Features

- **Automatic Cleanup**: Removes files older than 24 hours
- **Secure Processing**: Filename sanitization and validation
- **Error Handling**: Comprehensive error messages
- **Format Support**: `.xlsx` and `.xls` files

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)

### Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/excel-to-docx-converter.git
cd excel-to-docx-converter
```

2. **Create virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

### Dependencies

The project requires the following Python packages:

```txt
Flask==3.1.2
pandas==2.3.3
python-docx==1.1.0
openpyxl==3.1.5
Werkzeug==3.1.5
```

Create a `requirements.txt` file with the above content, or install manually:

```bash
pip install Flask pandas python-docx openpyxl Werkzeug
```

---

## Running the Project

### Development Mode

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000` with the following access points:

**Local Access:**
```
http://localhost:5000
```

**Network Access:**
```
http://[YOUR_LOCAL_IP]:5000
```

The application will automatically detect and display your local IP address on startup:

```
TRUY CẬP TỪ MÁY NÀY:
   → http://localhost:5000

TRUY CẬP TỪ MÁY KHÁC CÙNG MẠNG:
   → http://192.168.1.100:5000
```

### Production Deployment

For production environments, use a WSGI server like Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or with Docker:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

---

## Environment Configuration

### Application Settings

The application can be configured by modifying these constants in `app.py`:

```python
# File upload settings
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}
```

### Storage Configuration

```python
# Cleanup settings (in hours)
CLEANUP_INTERVAL = 24  # Clean files older than 24 hours
CLEANUP_CHECK_FREQUENCY = 3600  # Check every hour (in seconds)
```

### Network Configuration

```python
# Server settings
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000
DEBUG = False  # Set to True for development only
THREADED = True  # Enable multi-threading
```

### Environment Variables (Optional)

Create a `.env` file for environment-specific settings:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
MAX_FILE_SIZE=52428800
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
```

Load with `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Folder Structure

```
excel-to-docx-converter/
├── app.py                  # Main Flask application
├── excel_processor.py      # Excel processing logic
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── templates/
│   └── index.html         # Main UI template
│
├── uploads/               # Temporary Excel file storage (auto-created)
│   └── .gitkeep
│
├── outputs/               # Generated DOCX files (auto-created)
│   └── .gitkeep
│
└── static/                # Static assets (optional)
    ├── css/
    ├── js/
    └── images/
```

---

## API Reference

### Endpoints

#### `POST /upload`
Upload an Excel file and retrieve sheet names.

**Request:**
```http
POST /upload
Content-Type: multipart/form-data

file: [Excel file]
```

**Response:**
```json
{
  "filename": "example_20240114_153045.xlsx",
  "sheets": ["Sheet1", "Data", "Summary"],
  "file_size": "245.6 KB"
}
```

---

#### `POST /preview`
Preview data from a selected sheet.

**Request:**
```json
{
  "filename": "example_20240114_153045.xlsx",
  "sheet": "Sheet1",
  "num_rows": 10
}
```

**Response:**
```json
{
  "preview": [
    ["Header1", "Header2", "Header3"],
    ["Value1", "Value2", "Value3"]
  ],
  "total_rows": 150,
  "total_cols": 10
}
```

---

#### `POST /get-columns`
Retrieve column headers from a specific row.

**Request:**
```json
{
  "filename": "example_20240114_153045.xlsx",
  "sheet": "Sheet1",
  "header_row": 2
}
```

**Response:**
```json
{
  "columns": ["Name", "Email", "Phone", "Department"]
}
```

---

#### `POST /convert`
Convert selected columns to DOCX format.

**Request:**
```json
{
  "filename": "example_20240114_153045.xlsx",
  "sheet": "Sheet1",
  "columns": ["Name", "Email", "Phone"],
  "header_row": 2,
  "data_start_row": 3,
  "data_end_row": 100
}
```

**Response:**
```json
{
  "success": true,
  "output_file": "output_20240114_153045.docx",
  "row_count": 97,
  "column_count": 3,
  "message": "Đã xuất thành công 97 bản ghi với 3 cột"
}
```

---

#### `GET /download/<filename>`
Download a generated DOCX file.

**Request:**
```http
GET /download/output_20240114_153045.docx
```

**Response:**
```
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment; filename="output_20240114_153045.docx"

[Binary DOCX data]
```

</div>
