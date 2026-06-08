# tests/export/test_resume_docx.py

from __future__ import annotations

from pathlib import Path

import pytest

from src.export.resume_docx import export_materials_to_docx


def sample_materials_data() -> dict:
    return {
        "resume_bullets": [
            "Built JobFit-AI using Python and layered architecture.",
            "Integrated Google Sheets storage for structured application data.",
        ],
        "cover_letter": "Dear Hiring Manager, I am excited to apply.",
        "warnings": ["No direct React experience was found."],
    }


def test_export_materials_to_docx_creates_file(tmp_path):
    file_path = export_materials_to_docx(
        sample_materials_data(),
        output_dir=str(tmp_path),
        filename="test_resume.docx",
    )

    assert Path(file_path).exists()
    assert file_path.endswith(".docx")


def test_export_materials_to_docx_adds_extension(tmp_path):
    file_path = export_materials_to_docx(
        sample_materials_data(),
        output_dir=str(tmp_path),
        filename="test_resume",
    )

    assert Path(file_path).exists()
    assert file_path.endswith(".docx")


def test_export_materials_to_docx_rejects_missing_resume_bullets(tmp_path):
    data = sample_materials_data()
    data["resume_bullets"] = []

    with pytest.raises(ValueError):
        export_materials_to_docx(data, output_dir=str(tmp_path))


def test_export_materials_to_docx_rejects_missing_cover_letter(tmp_path):
    data = sample_materials_data()
    data["cover_letter"] = ""

    with pytest.raises(ValueError):
        export_materials_to_docx(data, output_dir=str(tmp_path))

def test_export_materials_to_docx_uses_new_name_if_file_exists(tmp_path):
    first_file_path = export_materials_to_docx(
        sample_materials_data(),
        output_dir=str(tmp_path),
        filename="test_resume.docx",
    )

    second_file_path = export_materials_to_docx(
        sample_materials_data(),
        output_dir=str(tmp_path),
        filename="test_resume.docx",
    )

    assert Path(first_file_path).exists()
    assert Path(second_file_path).exists()
    assert first_file_path != second_file_path
    assert second_file_path.endswith("_1.docx")