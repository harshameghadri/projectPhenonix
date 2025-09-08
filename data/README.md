# Data Directory

Place your professional documents in this directory for the VitaeAgent to process:

## Supported File Types

### Documents
- **PDFs**: Place your CV, resumes, certificates, project reports
- **Text Files**: `.txt` and `.md` files with professional content

### External Sources
- **blog_urls.txt**: List of your blog post URLs (one per line)
- **GitHub**: Configure `GITHUB_USERNAME` in your `.env` file

## Example Data Structure
```
data/
├── cv.pdf                    # Your main CV/resume
├── portfolio.pdf             # Project portfolio
├── certifications.pdf        # Professional certificates
├── project_reports.txt       # Technical project descriptions
├── skills_summary.md         # Skills and expertise overview
└── blog_urls.txt            # List of blog post URLs
```

## Getting Started

1. Copy your professional documents to this directory
2. Update `blog_urls.txt` with your blog post URLs
3. Set `GITHUB_USERNAME` in your `.env` file
4. Run the ingestion script: `python backend/scripts/ingest.py`

The VitaeAgent will process all these sources and create a comprehensive knowledge base for intelligent conversations about your professional background.