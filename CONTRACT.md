# CONTRACT.md (Short Teaching Template)

## Purpose

Use this file to map each functionality to component ownership and explicit interfaces.

## Part B: Architecture Mapping

For each functionality, map responsibilities to components.

### Job Description Analysis Mapping

- `interface` responsibilities:
  - Collect the pasted job description from the user.
  - Ask the user whether they want to save the analyzed job description.
  - Collect an application ID if the user chooses to save the analysis.
  - Send the job description, save choice, and application ID to the engine.
  - Display the extracted job title, skills, responsibilities, keywords, and save status.
- `engine` responsibilities:
  - Validate that the job description is not empty.
  - Reject input that does not appear to be a job description.
  - Send the job description to Gemini API.
  - Clean Gemini’s response if it includes JSON inside Markdown code fences.
  - Parse Gemini’s response into structured data.
  - If saving is requested, prepare the job analysis record and send it to storage.
  - Return success, failure, or save status to the interface.
- `storage` responsibilities:
  - Connect to the Google Sheet using `service_account.json`.
  - Save the analyzed job description when the engine requests it.
  - Check for duplicate `application_id` values before saving.
  - Return a storage status to indicate success, duplicate record, or error.

### User Profile Management Mapping

- `interface` responsibilities:
  - Collect the user profile information from the user.
  - Ask for the user's name, education, skills, projects, work experience, and leadership experience.
  - Send the structured user profile data to the engine.
  - Display success or error messages after the profile is saved or retrieved.
- `engine` responsibilities:
  - Validate that the user profile contains the required fields.
  - Prepare the user profile record for storage.
  - Send the user profile record to storage.
  - Retrieve the user profile from storage when needed for resume and cover letter generation.
  - Return success, failure, or retrieved profile data to the interface.
- `storage` responsibilities:
  - Save user profile data in the Google Sheet.
  - Check for duplicate `user_id` values before saving.
  - Retrieve a saved user profile when requested by the engine.
  - Return a storage status to indicate success, duplicate record, not found, or error.

### Resume and Cover Letter Generation Mapping

- `interface` responsibilities:
  - Collect the user profile information, including education, skills, projects, and job experience.
  - Send the user profile and analyzed job description to the engine.
  - Show the generated resume bullets and cover letter.
  - Allow the user to copy or edit the generated content.
  - Display errors when required information is missing.
- `engine` responsibilities:
  - Validate the user profile and job analysis.
  - Use Gemini API to generate resume bullets and a cover letter.
  - Ensure the generated content only uses information provided by the user.
  - Match the resume bullets and cover letter to the job title, required skills, responsibilities, and keywords.
  - Return structured generated content to the interface.
- `storage` responsibilities:
  - Save generated resume bullets and cover letter if the user saves the application.
  - Retrieve saved generated content for a previous application.

## Part C: Interface Contracts

### Job Description Analysis

#### `interface -> engine`

- Function(s):
  - `analyze_job_description(job_description: str) -> response_payload`
  - `analyze_and_optionally_save(job_description: str, application_id: int | str | None = None, save: bool = False) -> response_payload`
- Input payload:
  - `{"job_description": str}`
  - `{"job_description": str, "application_id": int | str | None, "save": bool}`
- Return payload/status:
  - `{"status": "success", "data": {"job_title": str, "required_skills": list[str], "preferred_skills": list[str], "responsibilities": list[str], "keywords": list[str]}}`
  - `{"status": "success", "data": {"job_title": str, "required_skills": list[str], "preferred_skills": list[str], "responsibilities": list[str], "keywords": list[str]}, "save_status": "success" | "exists" | "error"}`
- Failure statuses:
  - `{"status": "incomplete", "message": "Job description is required."}`
  - `{"status": "invalid_input", "message": "Input does not appear to be a job description."}`
  - `{"status": "ai_error", "message": "Could not analyze job description."}`
  - `{"status": "missing_application_id", "message": "Application ID is required to save the job analysis."}`

#### `engine -> storage`

- Function(s):
  - `save_job_analysis(job_analysis: job_analysis_record) -> storage_status`
  - `get_job_analysis(application_id: str) -> response_payload`
- Input payload:
  - `{"application_id": int | str, "job_title": str, "required_skills": list[str], "keywords": list[str]}`
- Return payload/status:
  - `"success"`
  - `"exists"`
  - `"error"`
  - `{"status": "success", "data": {"application_id": int | str, "job_title": str, "required_skills": list[str], "keywords": list[str]}}`
- Failure statuses:
  - `"exists"` means the `application_id` is already stored in the Google Sheet.
  - `"error"` means required fields were missing or the Google Sheet operation failed.
  - `{"status": "not_found", "message": "Job analysis record was not found."}`

### User Profile Management

#### `interface -> engine`

- Function(s):
  - `save_user_profile(user_profile: dict) -> response_payload`
  - `get_user_profile(user_id: int | str) -> response_payload`
- Input payload:
  - `{"user_id": int | str, "name": str, "education": str, "skills": list[str], "projects": list[str], "experience": list[str]}`
  - `{"user_id": int | str}`
- Return payload/status:
  - `{"status": "success", "save_status": "success"}`
  - `{"status": "success", "data": {"user_id": int | str, "name": str, "education": str, "skills": list[str], "projects": list[str], "experience": list[str]}}`
- Failure statuses:
  - `{"status": "exists", "message": "User profile already exists."}`
  - `{"status": "incomplete_profile", "message": "User profile is missing required information."}`
  - `{"status": "storage_error", "message": "Could not save user profile."}`
  - `{"status": "not_found", "message": "User profile was not found."}`

#### `engine -> storage`

- Function(s):
  - `save_user_profile(user_profile: user_profile_record) -> storage_status`
  - `get_user_profile(user_id: int | str) -> response_payload`
- Input payload:
  - `{"user_id": int | str, "name": str, "education": str, "skills": list[str], "projects": list[str], "experience": list[str]}`
  - `{"user_id": int | str}`
- Return payload/status:
  - `"success"`
  - `"exists"`
  - `"error"`
  - `{"status": "success", "data": {"user_id": int | str, "name": str, "education": str, "skills": list[str], "projects": list[str], "experience": list[str]}}`
- Failure statuses:
  - `"exists"` means the `user_id` is already stored in the Google Sheet.
  - `"error"` means required fields were missing or the Google Sheet operation failed.
  - `{"status": "not_found", "message": "User profile was not found."}`

### Resume and Cover Letter Generation

#### `interface -> engine`

- Function(s):
  - `generate_application_materials(user_profile: dict, job_analysis: dict) -> response_payload`
- Input payload:
  - `{"user_profile": {"name": str, "education": str, "skills": list[str], "projects": list[str], "experience": list[str]}, "job_analysis": {"job_title": str, "required_skills": list[str], "keywords": list[str]}}`
- Return payload/status:
  - `{"status": "success", "data": {"resume_bullets": list[str], "cover_letter": str, "warnings": list[str]}}`
- Failure statuses:
  - `{"status": "incomplete_profile", "message": "User profile is missing required information."}`
  - `{"status": "missing_job_analysis", "message": "Job analysis is required before generating materials."}`
  - `{"status": "generation_failed", "message": "Generated content was empty or invalid."}`
  - `{"status": "ai_error", "message": "Could not generate application materials."}`

#### `engine -> storage`

- Function(s):
  - `save_generated_materials(application_id: str, materials: generated_materials_record) -> response_payload`
  - `get_generated_materials(application_id: str) -> response_payload`
- Input payload:
  - `{"application_id": int | str, "user_id": int | str, "resume_bullets": list[str], "cover_letter": str}`
- Return payload/status:
  - Return payload/status:
  - `"success"`
  - `"exists"`
  - `"error"`
  - `{"status": "success", "data": {"application_id": int | str, "user_id": int | str, "resume_bullets": list[str], "cover_letter": str}}`
- Failure statuses:
  - `"exists"` means generated materials for that `application_id` are already stored.
  - `"error"` means required fields were missing or the Google Sheet operation failed.
  - `{"status": "not_found", "message": "Generated materials were not found."}`
