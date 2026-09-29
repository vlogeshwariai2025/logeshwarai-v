import os
from datetime import datetime
from fpdf import FPDF

EXPORT_FOLDER = os.path.join("static", "exports")
os.makedirs(EXPORT_FOLDER, exist_ok=True)
FONT_PATH = os.path.join("static", "fonts", "DejaVuSans.ttf")


class ComicPDF(FPDF):
    """Custom FPDF subclass with automated footer handling."""
    def footer(self):
        self.set_y(-12)
        font = "DejaVu" if "DejaVu" in self.fonts else "Helvetica"
        self.set_font(font, "", 8)
        self.cell(0, 8, f"ComicCraft AI Story Creator  -  Page {self.page_no()}", align="C")


def save_pdf(layout: list) -> str:
    """
    Compiles the comic layout into a multi-page PDF file using FPDF.
    Each panel's image and narrative text are placed onto consecutive pages.

    Args:
        layout (list): List of panel dictionaries containing panel number, title,
                       image path, text, scene description, etc.

    Returns:
        str: Relative path to the saved PDF file (e.g. static/exports/comic_20260925.pdf).
    """
    pdf = ComicPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Setup Unicode TrueType font
    font_name = "Helvetica"
    if os.path.exists(FONT_PATH):
        try:
            pdf.add_font("DejaVu", "", FONT_PATH)
            bold_font = os.path.join("static", "fonts", "DejaVuSans-Bold.ttf")
            if os.path.exists(bold_font):
                pdf.add_font("DejaVu", "B", bold_font)
            font_name = "DejaVu"
        except Exception as e:
            print(f"[WARNING] Could not load DejaVu font, falling back to Helvetica: {e}")
            font_name = "Helvetica"

    for panel in layout:
        # Determine valid disk path for image
        raw_img = panel.get("raw_image_path") or panel.get("image_path", "")
        # Remove leading slashes for local filesystem resolution
        clean_img_path = raw_img.lstrip("/\\")
        story_text = panel.get("text", "")

        pdf.add_page()

        # Panel Title Header
        title_text = f"Panel {panel.get('panel', '')}: {panel.get('title', '')}"
        if font_name == "Helvetica":
            title_text = title_text.encode("latin-1", "replace").decode("latin-1")

        pdf.set_font(font_name, "B" if font_name == "Helvetica" else "", 14)
        pdf.cell(0, 10, title_text, new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(1)

        # Image placement
        y_image = 26
        image_height = 95
        spacing_after_image = 10

        if os.path.exists(clean_img_path):
            try:
                # Center image on page
                img_width = pdf.w - 30
                pdf.image(clean_img_path, x=15, y=y_image, w=img_width, h=image_height)
            except Exception as e:
                pdf.set_y(y_image)
                pdf.set_font(font_name, "", 10)
                pdf.multi_cell(0, 8, f"[Image display error: {e}]")
        else:
            pdf.set_y(y_image)
            pdf.set_font(font_name, "", 10)
            pdf.multi_cell(0, 8, f"[Image missing: {clean_img_path}]")

        # Text placement below image
        pdf.set_y(y_image + image_height + spacing_after_image)
        pdf.set_font(font_name, "", 10)

        # Clean markdown asterisks and format lines
        story_lines = story_text.strip().splitlines()
        if story_lines and story_lines[0].strip().lower().startswith("**panel"):
            story_lines = story_lines[1:]

        cleaned_text = "\n".join(story_lines).strip()
        cleaned_text = cleaned_text.replace("**CAPTION:**", "CAPTION:").replace("**NARRATION:**", "NARRATION:").replace("**", "")

        if font_name == "Helvetica":
            cleaned_text = cleaned_text.encode("latin-1", "replace").decode("latin-1")

        pdf.multi_cell(0, 6, cleaned_text)

    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    pdf_path = os.path.join(EXPORT_FOLDER, filename)
    pdf.output(pdf_path)

    print(f"[SUCCESS] PDF compiled and exported to: {pdf_path}")
    return pdf_path.replace("\\", "/")

