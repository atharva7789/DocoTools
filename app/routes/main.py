from flask import Blueprint, render_template, request, send_file, jsonify, abort, current_app
from pathlib import Path
from werkzeug.utils import secure_filename
from pypdf import PdfReader, PdfWriter
from PIL import Image
import fitz
import openpyxl
from pptx import Presentation
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import shutil
import uuid
import re
import math
import subprocess
import tempfile

main = Blueprint("main", __name__)

ALLOWED = {
    "merge": {".pdf"},
    "split": {".pdf"},
    "compress": {".pdf"},
    "jpg-pdf": {".jpg", ".jpeg", ".png"},
    "pdf-jpg": {".pdf"},
    "pdf-word": {".pdf"},
    "pdf-ppt": {".pdf"},
    "pdf-excel": {".pdf"},
    "ppt-pdf": {".pptx", ".ppt"},
    "excel-pdf": {".xlsx", ".xls"},
}

TOOL_INFO = {
    "merge": ("Merge PDF", "Combine multiple PDF files into one organized document."),
    "split": ("Split PDF", "Separate pages from a PDF into individual files."),
    "compress": ("Compress PDF", "Reduce PDF file size while keeping your document usable."),
    "jpg-pdf": ("JPG → PDF", "Turn one or multiple images into a PDF document."),
    "pdf-jpg": ("PDF → JPG", "Convert PDF pages into high-quality JPG images."),
    "pdf-word": ("PDF → Word", "Convert PDF text into an editable Word document."),
    "pdf-ppt": ("PDF → PowerPoint", "Turn PDF pages into a PowerPoint presentation."),
    "pdf-excel": ("PDF → Excel", "Extract PDF text into an Excel spreadsheet."),
    "ppt-pdf": ("PowerPoint → PDF", "Convert PowerPoint text and slides into a PDF."),
    "excel-pdf": ("Excel → PDF", "Convert spreadsheet data into a clean PDF."),
    "summarizer": ("AI Summarizer", "Extract the important ideas from your document and create a concise summary."),
}


def upload_root():
    return Path(current_app.config["UPLOAD_ROOT"])


def new_job():
    job = uuid.uuid4().hex
    folder = upload_root() / job
    folder.mkdir(parents=True, exist_ok=True)
    return job, folder


def safe_name(name):
    name = secure_filename(name or "file")
    return name or "file"


def get_files(request_files, tool):
    files = [f for f in request_files if f and f.filename]
    if not files:
        raise ValueError("Please select at least one file.")
    allowed = ALLOWED[tool]
    bad = [f.filename for f in files if Path(f.filename).suffix.lower() not in allowed]
    if bad:
        raise ValueError(f"Unsupported file type: {bad[0]}")
    return files


def send_result(job, path):
    return jsonify({
        "success": True,
        "job": job,
        "download": f"/download/{job}/{path.name}",
        "filename": path.name,
    })


@main.route("/")
def home():
    return render_template("index.html", tools=TOOL_INFO)


@main.route("/tool/<tool>")
def tool_page(tool):
    if tool not in TOOL_INFO:
        abort(404)
    title, description = TOOL_INFO[tool]
    return render_template("tool.html", tool=tool, title=title, description=description)


@main.route("/process/<tool>", methods=["POST"])
def process(tool):
    if tool not in ALLOWED and tool != "summarizer":
        return jsonify(success=False, error="Unknown tool."), 404

    job, folder = new_job()

    try:
        if tool == "summarizer":
            files = get_files(request.files.getlist("files"), "pdf-jpg")
            src = folder / safe_name(files[0].filename)
            files[0].save(src)
            text = extract_pdf_text(src)
            summary = summarize(text)
            out = folder / "DocoTools_Summary.txt"
            out.write_text(summary, encoding="utf-8")
            return send_result(job, out)

        files = get_files(request.files.getlist("files"), tool)

        for i, f in enumerate(files):
            dest = folder / f"{i}_{safe_name(f.filename)}"
            f.save(dest)

        inputs = sorted(folder.glob("*"))

        if tool == "merge":
            if len(inputs) < 2:
                raise ValueError("Select at least two PDF files.")
            out = folder / "DocoTools_Merged.pdf"
            writer = PdfWriter()
            for p in inputs:
                reader = PdfReader(str(p))
                for page in reader.pages:
                    writer.add_page(page)
            with out.open("wb") as fh:
                writer.write(fh)

        elif tool == "split":
            reader = PdfReader(str(inputs[0]))
            out_dir = folder / "split"
            out_dir.mkdir()
            for i, page in enumerate(reader.pages, 1):
                writer = PdfWriter()
                writer.add_page(page)
                with (out_dir / f"page_{i}.pdf").open("wb") as fh:
                    writer.write(fh)
            shutil.make_archive(str(folder / "DocoTools_Split"), "zip", out_dir)
            out = folder / "DocoTools_Split.zip"

        elif tool == "compress":
            reader = PdfReader(str(inputs[0]))
            writer = PdfWriter()
            for page in reader.pages:
                page.compress_content_streams()
                writer.add_page(page)
            out = folder / "DocoTools_Compressed.pdf"
            with out.open("wb") as fh:
                writer.write(fh)

        elif tool == "jpg-pdf":
            images = []
            for p in inputs:
                im = Image.open(p).convert("RGB")
                images.append(im)
            out = folder / "DocoTools_Images.pdf"
            images[0].save(out, save_all=True, append_images=images[1:])

        elif tool == "pdf-jpg":
            src = inputs[0]
            out_dir = folder / "pdf_jpg"
            out_dir.mkdir()
            doc = fitz.open(src)
            for i, page in enumerate(doc, 1):
                pix = page.get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False)
                pix.save(str(out_dir / f"page_{i}.jpg"))
            doc.close()
            shutil.make_archive(str(folder / "DocoTools_PDF_JPG"), "zip", out_dir)
            out = folder / "DocoTools_PDF_JPG.zip"

        elif tool == "pdf-word":
            out = pdf_to_docx(inputs[0], folder)

        elif tool == "pdf-ppt":
            out = pdf_to_ppt(inputs[0], folder)

        elif tool == "pdf-excel":
            out = pdf_to_excel(inputs[0], folder)

        elif tool == "ppt-pdf":
            out = ppt_to_pdf(inputs[0], folder)

        elif tool == "excel-pdf":
            out = excel_to_pdf(inputs[0], folder)

        # Remove uploaded source files immediately after processing.
        for p in list(folder.iterdir()):
            if p.is_file() and p != out:
                try:
                    p.unlink()
                except OSError:
                    pass

        return send_result(job, out)

    except Exception as exc:
        shutil.rmtree(folder, ignore_errors=True)
        return jsonify(success=False, error=str(exc) or "Processing failed."), 400


def extract_pdf_text(path):
    doc = fitz.open(path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.strip()


def summarize(text, max_sentences=6):
    if not text:
        return "No readable text was found in the PDF."
    text = re.sub(r"\s+", " ", text)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    if len(sentences) <= max_sentences:
        return "\n\n".join(sentences)

    words = re.findall(r"[A-Za-z]{3,}", text.lower())
    stop = {"the","and","for","that","with","this","from","are","was","were","have","has","into","your","you","will","about","their","they","there","which","using","also","than","then","been","but","not","can","its","our"}
    freq = {}
    for w in words:
        if w not in stop:
            freq[w] = freq.get(w, 0) + 1

    scored = []
    for idx, s in enumerate(sentences):
        sw = re.findall(r"[A-Za-z]{3,}", s.lower())
        score = sum(freq.get(w, 0) for w in sw) / max(1, len(sw))
        scored.append((score, idx, s))
    chosen = sorted(scored, reverse=True)[:max_sentences]
    chosen = sorted(chosen, key=lambda x: x[1])
    return "\n\n".join(x[2] for x in chosen)


def pdf_to_docx(src, folder):
    try:
        from docx import Document
    except ImportError:
        raise ValueError("PDF → Word requires python-docx. Run pip install -r requirements.txt.")
    doc = fitz.open(src)
    out = folder / "DocoTools_Word.docx"
    word = Document()
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            for line in text.splitlines():
                word.add_paragraph(line)
        if i < len(doc) - 1:
            word.add_page_break()
    word.save(out)
    doc.close()
    return out


def pdf_to_ppt(src, folder):
    doc = fitz.open(src)
    prs = Presentation()
    blank = prs.slide_layouts[6]
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(1.3, 1.3), alpha=False)
        img = folder / f"slide_{len(prs.slides)+1}.png"
        pix.save(str(img))
        slide = prs.slides.add_slide(blank)
        slide.shapes.add_picture(str(img), 0, 0, width=prs.slide_width, height=prs.slide_height)
    out = folder / "DocoTools_PowerPoint.pptx"
    prs.save(out)
    doc.close()
    return out


def pdf_to_excel(src, folder):
    doc = fitz.open(src)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "PDF Text"
    row = 1
    for page_no, page in enumerate(doc, 1):
        ws.cell(row, 1, f"Page {page_no}")
        row += 1
        for line in page.get_text().splitlines():
            if line.strip():
                ws.cell(row, 1, line.strip())
                row += 1
        row += 1
    out = folder / "DocoTools_Excel.xlsx"
    wb.save(out)
    doc.close()
    return out



def libreoffice_convert(src, folder):
    """Use LibreOffice when available for high-fidelity office conversions."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return None
    try:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(folder), str(src)],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120
        )
        generated = folder / (Path(src).stem + ".pdf")
        return generated if generated.exists() else None
    except Exception:
        return None


def ppt_to_pdf(src, folder):
    converted = libreoffice_convert(src, folder)
    if converted:
        return converted

    # Fallback keeps all slide text readable when LibreOffice is unavailable.
    prs = Presentation(src)
    out = folder / "DocoTools_PowerPoint.pdf"
    c = canvas.Canvas(str(out), pagesize=landscape(A4))
    W, H = landscape(A4)
    for slide in prs.slides:
        c.setFont("Helvetica-Bold", 18)
        y = H - 45
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                for line in shape.text.splitlines():
                    c.drawString(35, y, line[:110])
                    y -= 22
                    if y < 35:
                        c.showPage()
                        y = H - 45
                        c.setFont("Helvetica", 9)
        c.showPage()
    c.save()
    return out


def excel_to_pdf(src, folder):
    converted = libreoffice_convert(src, folder)
    if converted:
        return converted

    # Fallback retains all cell values when LibreOffice is unavailable.
    wb = openpyxl.load_workbook(src, data_only=False)
    out = folder / "DocoTools_Excel.pdf"
    c = canvas.Canvas(str(out), pagesize=A4)
    W, H = A4
    for ws in wb.worksheets:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(35, H - 38, ws.title)
        y = H - 62
        c.setFont("Helvetica", 7)
        for row in ws.iter_rows(values_only=True):
            values = ["" if v is None else str(v) for v in row]
            line = " | ".join(values)
            c.drawString(35, y, line[:130])
            y -= 11
            if y < 30:
                c.showPage()
                y = H - 38
                c.setFont("Helvetica", 7)
        c.showPage()
    c.save()
    return out


@main.route("/download/<job>/<filename>")
def download(job, filename):
    folder = upload_root() / job
    path = folder / secure_filename(filename)
    if not path.exists() or not path.is_file():
        abort(404)
    return send_file(path, as_attachment=True, download_name=path.name)


@main.route("/delete/<job>", methods=["POST"])
def delete_job(job):
    folder = upload_root() / secure_filename(job)
    if not folder.exists():
        return jsonify(success=True, message="File already deleted.")
    shutil.rmtree(folder, ignore_errors=True)
    return jsonify(success=True, message="Your files were deleted from DocoTools storage.")
