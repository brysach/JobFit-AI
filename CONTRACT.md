# CONTRACT.md (Short Teaching Template)

## Purpose

Use this file to map each functionality to component ownership and explicit interfaces.

## Part B: Architecture Mapping

For each functionality, map responsibilities to components.

### Job Description Analysis Mapping

- `interface` responsibilities:
  - Collect the pasted job description from the user.
  - Ask the user whether they want to save the analyzed job description.
  - Send the job description and save choice to the engine.
  - Display the extracted job title, skills, responsibilities, keywords, save status, and generated `application_id`.

- `engine` responsibilities:
  - Validate that the job description is not empty.
  - Reject input that does not appear to be a job description.
  - Send the job description to Gemini API.
  - Clean Gemini’s response if it includes JSON inside Markdown code fences.
  - Parse Gemini’s response into structured data.
  - If saving is requested, prepare the job analysis record and send it to storage.
  - Return success, failure, save status, or generated `application_id` to the interface.

- `storage` responsibilities:
  - Connect to the Google Sheet using `service_account.json`.
  - Save the analyzed job description when the engine requests it.
  - Generate a new `application_id` using the existing saved records.
  - Retrieve a saved job analysis when requested by the engine.
  - Return a storage response to indicate success, generated ID, not found, or error.

### User Profile Management Mapping

- `interface` responsibilities:
  - Collect the user profile information from the user.
  - Ask for the user's name, education, skills, projects, work experience, and leadership experience.
  - Send the structured user profile data to the engine.
  - Display success or error messages after the profile is saved or retrieved.
  - Display the generated `user_id` after a profile is saved successfully.

- `engine` responsibilities:
  - Validate that the user profile contains the required fields.
  - Prepare the user profile record for storage.
  - Send the user profile record to storage.
  - Retrieve the user profile from storage when needed for resume and cover letter generation.
  - Return success, failure, generated `user_id`, or retrieved profile data to the interface.

- `storage` responsibilities:
  - Save user profile data in the Google Sheet.
  - Generate a new `user_id` using the existing saved records.
  - Retrieve a saved user profile when requested by the engine.
  - Return a storage response to indicate success, generated ID, not found, or error.

### Resume and Cover Letter Generation Mapping

- `interface` responsibilities:
  - Ask the user for a saved `user_id` and saved `application_id`.
  - Ask the user whether they want to save the generated materials.
  - Send the `user_id`, `application_id`, and save choice to the engine.
  - Show the generated resume bullets, cover letter, warnings, and save status.
  - Ask the user whether they want to export the generated materials to a `.docx` file.
  - Display the saved `.docx` file path or an export error message.

- `engine` responsibilities:
  - Retrieve the saved user profile from storage.
  - Retrieve the saved job analysis from storage.
  - Validate the user profile and job analysis.
  - Use Gemini API to generate resume bullets and a cover letter.
  - Ensure the generated content only uses information provided by the user.
  - Match the resume bullets and cover letter to the job title, required skills, responsibilities, and keywords.
  - If saving is requested, prepare the generated materials record and send it to storage.
  - Return structured generated content, warnings, and save status to the interface.

- `storage` responsibilities:
  - Save generated resume bullets and cover letter if the engine requests it.
  - Retrieve saved generated content for a previous application.
  - Return a storage status to indicate success, duplicate record, not found, or error.

## Part C: Interface Contracts

### Job Description Analysis

#### `interface -> engine`

- Function(s):
  - `analyze_job_description(job_description: str) -> response_payload`
  - `analyze_and_optionally_save(job_description: str, application_id: int | str | None = None, save: bool = False) -> response_payload`

- Input payload:
  - `{"job_description": str}`
  - `{"job_description": str, "save": bool}`

- Return payload/status:
  - `{"status": "success", "data": {"job_title": str, "required_skills": list[str], "preferred_skills": list[str], "responsibilities": list[str], "keywords": list[str]}}`
  - `{"status": "success", "data": {"job_title": str, "required_skills": list[str], "preferred_skills": list[str], "responsibilities": list[str], "keywords": list[str]}, "save_status": "success" | "error", "application_id": int}`

- Failure statuses:
  - `{"status": "incomplete", "message": "Job description is required."}`
  - `{"status": "invalid_input", "message": "Input does not appear to be a job description."}`
  - `{"status": "ai_error", "message": "Could not analyze job description."}`

#### `engine -> storage`

- Function(s):
  - `save_job_analysis(job_analysis: job_analysis_record) -> response_payload`
  - `get_job_analysis(application_id: int | str) -> response_payload`

- Input payload:
  - `{"job_title": str, "required_skills": list[str], "keywords": list[str]}`
  - `{"application_id": int | str}`

- Return payload/status:
  - `{"status": "success", "application_id": int}`
  - `{"status": "error"}`
  - `{"status": "success", "data": {"application_id": int | str, "job_title": str, "required_skills": list[str], "keywords": list[str]}}`

- Failure statuses:
  - `{"status": "error"}` means required fields were missing or the Google Sheet operation failed.
  - `{"status": "not_found", "message": "Job analysis record was not found."}`

### User Profile Management

#### `interface -> engine`

- Function(s):
  - `save_user_profile(user_profile: dict) -> response_payload`
  - `get_user_profile(user_id: int | str) -> response_payload`

- Input payload:
  - `{"name": str, "education": str, "skills": list[str], "projects": list[str], "experience": list[str]}`
  - `{"user_id": int | str}`

- Return payload/status:
  - `{"status": "success", "save_status": "success", "user_id": int}`
  - `{"status": "success", "data": {"user_id": int | str, "name": str, "education": str, "skills": list[str], "projects": list[str], "experience": list[str]}}`

- Failure statuses:
  - `{"status": "incomplete_profile", "message": "User profile is missing required information."}`
  - `{"status": "storage_error", "message": "Could not save user profile."}`
  - `{"status": "not_found", "message": "User profile was not found."}`

#### `engine -> storage`

- Function(s):
  - `save_user_profile(user_profile: user_profile_record) -> response_payload`
  - `get_user_profile(user_id: int | str) -> response_payload`

- Input payload:
  - `{"name": str, "education": str, "skills": list[str], "projects": list[str], "experience": list[str]}`
  - `{"user_id": int | str}`

- Return payload/status:
  - `{"status": "success", "user_id": int}`
  - `{"status": "error"}`
  - `{"status": "success", "data": {"user_id": int | str, "name": str, "education": str, "skills": list[str], "projects": list[str], "experience": list[str]}}`

- Failure statuses:
  - `{"status": "error"}` means required fields were missing or the Google Sheet operation failed.
  - `{"status": "not_found", "message": "User profile was not found."}`

### Resume and Cover Letter Generation

#### `interface -> engine`

- Function(s):
  - `generate_application_materials(user_profile: dict, job_analysis: dict) -> response_payload`
  - `generate_materials_for_saved_records(user_id: int | str, application_id: int | str, save: bool = False) -> response_payload`

- Input payload:
  - `{"user_profile": {"name": str, "education": str, "skills": list[str], "projects": list[str], "experience": list[str]}, "job_analysis": {"job_title": str, "required_skills": list[str], "keywords": list[str]}}`
  - `{"user_id": int | str, "application_id": int | str, "save": bool}`

- Return payload/status:
  - `{"status": "success", "data": {"resume_bullets": list[str], "cover_letter": str, "warnings": list[str]}}`
  - `{"status": "success", "data": {"resume_bullets": list[str], "cover_letter": str, "warnings": list[str]}, "save_status": "success" | "exists" | "error"}`

- Failure statuses:
  - `{"status": "incomplete_profile", "message": "User profile is missing required information."}`
  - `{"status": "missing_job_analysis", "message": "Job analysis is required before generating materials."}`
  - `{"status": "generation_failed", "message": "Generated content was empty or invalid."}`
  - `{"status": "ai_error", "message": "Could not generate application materials."}`

#### `engine -> storage`

- Function(s):
  - `save_generated_materials(materials: generated_materials_record) -> storage_status`
  - `get_generated_materials(application_id: int | str) -> response_payload`

- Input payload:
  - `{"application_id": int | str, "user_id": int | str, "resume_bullets": list[str], "cover_letter": str}`
  - `{"application_id": int | str}`

- Return payload/status:
  - `"success"`
  - `"exists"`
  - `"error"`
  - `{"status": "success", "data": {"application_id": int | str, "user_id": int | str, "resume_bullets": list[str], "cover_letter": str}}`

- Failure statuses:
  - `"exists"` means generated materials for that `application_id` are already stored.
  - `"error"` means required fields were missing or the Google Sheet operation failed.
  - `{"status": "not_found", "message": "Generated materials were not found."}`

#### `interface -> export`

- Function(s):
  - `export_materials_to_docx(materials_data: dict, output_dir: str = "outputs", filename: str | None = None) -> str`

- Input payload:
  - `{"resume_bullets": list[str], "cover_letter": str, "warnings": list[str]}`

- Return payload/status:
  - `"outputs/<generated_filename>.docx"`

- Failure statuses:
  - `ValueError` if resume bullets or cover letter are missing.
  - `PermissionError` if the file cannot be written because it is open or blocked by the operating system.
  - General export error if the `.docx` file cannot be created.
