# src/storage/storage_handler.py

from __future__ import annotations

from src.storage.job_analysis_storage import get_job_analysis
from src.storage.job_analysis_storage import save_job_analysis
from src.storage.materials_storage import get_generated_materials
from src.storage.materials_storage import save_generated_materials
from src.storage.user_profile_storage import get_user_profile
from src.storage.user_profile_storage import save_user_profile


__all__ = [
    "save_job_analysis",
    "get_job_analysis",
    "save_user_profile",
    "get_user_profile",
    "save_generated_materials",
    "get_generated_materials",
]