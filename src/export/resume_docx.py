# src/export/resume_docx.py

from __future__ import annotations

from pathlib import Path

from docx import Document


def _get_available_file_path(output_dir: str, filename: str) -> Path:
    """Return a file path that does not already exist."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not filename.endswith(".docx"):
        filename += ".docx"

    file_path = output_path / filename

    if not file_path.exists():
        return file_path

    stem = file_path.stem
    suffix = file_path.suffix

    counter = 1

    while True:
        new_file_path = output_path / f"{stem}_{counter}{suffix}"

        if not new_file_path.exists():
            return new_file_path

        counter += 1


def export_materials_to_docx(
    materials_data: dict,
    output_dir: str = "outputs",
    filename: str | None = None,
) -> str:
    """Export generated resume bullets and cover letter to a .docx file."""

    resume_bullets = materials_data.get("resume_bullets", [])
    cover_letter = materials_data.get("cover_letter", "")
    warnings = materials_data.get("warnings", [])

    if not isinstance(resume_bullets, list) or not resume_bullets:
        raise ValueError("resume_bullets must be a non-empty list.")

    if not isinstance(cover_letter, str) or cover_letter.strip() == "":
        raise ValueError("cover_letter must be a non-empty string.")

    if filename is None:
        filename = "generated_resume_materials.docx"

    file_path = _get_available_file_path(output_dir, filename)

    document = Document()

    document.add_heading("Generated Resume Materials", level=1)

    document.add_heading("Resume Bullets", level=2)
    for bullet in resume_bullets:
        document.add_paragraph(str(bullet), style="List Bullet")

    document.add_heading("Cover Letter", level=2)
    document.add_paragraph(cover_letter)

    if warnings:
        document.add_heading("Warnings", level=2)
        for warning in warnings:
            document.add_paragraph(str(warning), style="List Bullet")

    document.save(file_path)

    return str(file_path)