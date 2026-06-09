# tests/interface/test_materials_cli.py

from __future__ import annotations

import builtins

import src.interface.materials_cli as materials_cli


def sample_success_response() -> dict:
    return {
        "status": "success",
        "data": {
            "resume": {
                "skills": ["Python", "Git"],
                "projects": [
                    "Built JobFit-AI using Python, Git, and layered architecture."
                ],
                "experience": [
                    "Tutored students in problem-solving and communication."
                ],
            },
            "cover_letter": "Dear TechStart Hiring Team, I am excited to apply.",
            "strengths": [
                "Use your Python and Git experience to explain your project workflow."
            ],
            "weaknesses": [
                "Practice technical assessment questions before interviewing."
            ],
        },
    }


def sample_user_profiles_response() -> dict:
    return {
        "status": "success",
        "data": [
            {
                "row_number": 2,
                "user_id": 10,
                "name": "Bryan Estrada",
                "email": "bryan@example.com",
                "phone_number": "555-123-4567",
                "university": "University of California, Riverside",
                "degree": "B.S. Computer Science",
                "skills": ["Python", "Git"],
                "projects": ["JobFit-AI"],
                "experience": ["Math tutor"],
            },
            {
                "row_number": 3,
                "user_id": 11,
                "name": "Sofia Martinez",
                "email": "sofia@example.com",
                "phone_number": "555-987-6543",
                "university": "California State University, Fullerton",
                "degree": "B.S. Information Systems",
                "skills": ["Java", "SQL"],
                "projects": ["Inventory Tracker"],
                "experience": ["Retail associate"],
            },
        ],
    }


def sample_job_analyses_response() -> dict:
    return {
        "status": "success",
        "data": [
            {
                "row_number": 2,
                "application_id": 20,
                "company_name": "TechStart",
                "job_title": "Software Engineering Intern",
                "required_skills": ["Python", "Git"],
                "keywords": ["Python", "teamwork"],
            },
            {
                "row_number": 3,
                "application_id": 21,
                "company_name": "DataWorks",
                "job_title": "Data Analyst Intern",
                "required_skills": ["SQL", "Excel"],
                "keywords": ["data", "dashboard"],
            },
        ],
    }


def test_format_materials_response_success():
    output = materials_cli.format_materials_response(sample_success_response())

    assert "Generated Application Materials" in output
    assert "Resume Preview" in output
    assert "Skills:" in output
    assert "- Python" in output
    assert "Projects:" in output
    assert "- Built JobFit-AI using Python, Git, and layered architecture." in output
    assert "Experience:" in output
    assert "- Tutored students in problem-solving and communication." in output
    assert "Cover Letter:" in output
    assert "Dear TechStart Hiring Team" in output
    assert "Strengths:" in output
    assert "- Use your Python and Git experience to explain your project workflow." in output
    assert "Weaknesses:" in output
    assert "- Practice technical assessment questions before interviewing." in output


def test_format_materials_response_with_save_status():
    response = sample_success_response()
    response["save_status"] = "success"

    output = materials_cli.format_materials_response(response)

    assert "Save Status: success" in output


def test_format_materials_response_error():
    response = {
        "status": "missing_job_analysis",
        "message": "Job analysis is required before generating materials.",
    }

    output = materials_cli.format_materials_response(response)

    assert output == "Job analysis is required before generating materials."


def test_run_resume_generation_flow(monkeypatch):
    inputs = iter(
        [
            "1",
            "y",
            "2",
            "y",
            "y",
            "n",
        ]
    )

    captured_call = {}

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_generate_materials_for_saved_records(
        user_id: int | str,
        application_id: int | str,
        save: bool = False,
    ) -> dict:
        captured_call["user_id"] = user_id
        captured_call["application_id"] = application_id
        captured_call["save"] = save

        response = sample_success_response()
        response["save_status"] = "success"
        return response

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "list_job_analyses",
        lambda: sample_job_analyses_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "generate_materials_for_saved_records",
        fake_generate_materials_for_saved_records,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "success"
    assert result["save_status"] == "success"
    assert captured_call["user_id"] == 10
    assert captured_call["application_id"] == 21
    assert captured_call["save"] is True


def test_run_resume_generation_flow_user_selection_not_confirmed(monkeypatch):
    inputs = iter(["1", "n"])
    generate_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_generate_materials_for_saved_records(
        user_id: int | str,
        application_id: int | str,
        save: bool = False,
    ) -> dict:
        nonlocal generate_was_called
        generate_was_called = True
        return sample_success_response()

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "generate_materials_for_saved_records",
        fake_generate_materials_for_saved_records,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "cancelled"
    assert result["message"] == "Resume generation cancelled."
    assert generate_was_called is False


def test_run_resume_generation_flow_back_from_user_selection(monkeypatch):
    inputs = iter(["BACK"])
    generate_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_generate_materials_for_saved_records(
        user_id: int | str,
        application_id: int | str,
        save: bool = False,
    ) -> dict:
        nonlocal generate_was_called
        generate_was_called = True
        return sample_success_response()

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "generate_materials_for_saved_records",
        fake_generate_materials_for_saved_records,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "cancelled"
    assert result["message"] == "Returned to main menu."
    assert generate_was_called is False


def test_run_resume_generation_flow_invalid_user_selection(monkeypatch):
    inputs = iter(["99"])
    generate_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_generate_materials_for_saved_records(
        user_id: int | str,
        application_id: int | str,
        save: bool = False,
    ) -> dict:
        nonlocal generate_was_called
        generate_was_called = True
        return sample_success_response()

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "generate_materials_for_saved_records",
        fake_generate_materials_for_saved_records,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "invalid_selection"
    assert result["message"] == "Please choose a valid entry number."
    assert generate_was_called is False


def test_run_resume_generation_flow_invalid_job_selection(monkeypatch):
    inputs = iter(["1", "y", "99"])
    generate_was_called = False

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    def fake_generate_materials_for_saved_records(
        user_id: int | str,
        application_id: int | str,
        save: bool = False,
    ) -> dict:
        nonlocal generate_was_called
        generate_was_called = True
        return sample_success_response()

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "list_job_analyses",
        lambda: sample_job_analyses_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "generate_materials_for_saved_records",
        fake_generate_materials_for_saved_records,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "invalid_selection"
    assert result["message"] == "Please choose a valid entry number."
    assert generate_was_called is False


def test_run_resume_generation_flow_missing_user_id(monkeypatch):
    inputs = iter(["1"])
    users_response = sample_user_profiles_response()
    users_response["data"][0]["user_id"] = None

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: users_response,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "invalid_selection"
    assert result["message"] == "Selected user profile is missing its user ID."


def test_run_resume_generation_flow_missing_application_id(monkeypatch):
    inputs = iter(["1", "y", "1"])
    jobs_response = sample_job_analyses_response()
    jobs_response["data"][0]["application_id"] = None

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "list_job_analyses",
        lambda: jobs_response,
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "invalid_selection"
    assert result["message"] == "Selected job analysis is missing its application ID."


def test_run_resume_generation_flow_no_user_profiles(monkeypatch):
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: {
            "status": "success",
            "data": [],
        },
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "not_found"
    assert result["message"] == "No user profiles were found."


def test_run_resume_generation_flow_no_job_analyses(monkeypatch):
    inputs = iter(["1", "y"])

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(
        materials_cli,
        "list_user_profiles",
        lambda: sample_user_profiles_response(),
    )
    monkeypatch.setattr(
        materials_cli,
        "list_job_analyses",
        lambda: {
            "status": "success",
            "data": [],
        },
    )

    result = materials_cli.run_resume_generation_flow()

    assert result["status"] == "not_found"
    assert result["message"] == "No job analyses were found."