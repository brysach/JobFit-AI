# CONTRACT.md

## Purpose

Use this file to map each functionality to component ownership and explicit interfaces.

## Part B: Architecture Mapping

For each functionality, map responsibilities to components.

### Job Description Analysis Mapping

- `interface` responsibilities:
  - Collect the pasted job description from the user.
  - Ask the user whether they want to generate the analyzed job description.
  - Ask the user whether they want to save the analyzed job description.
  - Send the job description and save choice to the engine.
  - Display the extracted company name, job title, skills, responsibilities, keywords, and save status.

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
  - List saved job analyses when requested by the engine.
  - Delete a saved job analysis when requested by the engine.
  - Return a storage response to indicate success, generated ID, not found, or error.

### User Profile Management Mapping

- `interface` responsibilities:
  - Collect the user profile information from the user.
  - Ask for the user's name, email, phone number, university, degree, skills, projects, and experience.
  - Send the structured user profile data to the engine.
  - Display success or error messages after the profile is saved or retrieved.
  - Keep backend IDs hidden from normal user-facing output unless they are needed internally.

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
  - List saved user profiles when requested by the engine.
  - Delete a saved user profile when requested by the engine.
  - Return a storage response to indicate success, generated ID, not found, or error.

### Resume and Cover Letter Generation Mapping

- `interface` responsibilities:
  - Display saved user profiles and ask the user to select one.
  - Display the selected user profile details and ask for confirmation.
  - Display saved job analyses and ask the user to select one.
  - Display the selected job analysis details and ask for confirmation.
  - Ask the user whether they want to save the generated materials.
  - Send the selected `user_id`, selected `application_id`, and save choice to the engine.
  - Show the generated resume sections, cover letter, strengths, weaknesses, and save status.
  - Ask the user whether they want to export the generated materials to a `.docx` file.
  - Display the saved `.docx` file path or an export error message.

- `engine` responsibilities:
  - Retrieve the saved user profile from storage.
  - Retrieve the saved job analysis from storage.
  - Validate the user profile and job analysis.
  - Use Gemini API to generate resume skills, resume projects, resume experience, a cover letter, strengths, and weaknesses.
  - Ensure the generated content only uses information provided by the user.
  - Match the resume content and cover letter to the company name, job title, required skills, responsibilities, and keywords.
  - If saving is requested, prepare the generated materials record and send it to storage.
  - Return structured generated content, strengths, weaknesses, and save status to the interface.

- `storage` responsibilities:
  - Save generated resume sections, cover letter, strengths, and weaknesses if the engine requests it.
  - Retrieve saved generated content for a previous application.
  - Return a storage status to indicate success, duplicate record, not found, or error.

### Manage Saved User Profiles Mapping

- `interface` responsibilities:
  - Ask the engine for the saved user profiles.
  - Display a summarized list of saved user profiles.
  - Ask the user to select a profile from the displayed list.
  - Display the full selected user profile.
  - Ask the user to confirm deletion.
  - Display success, cancellation, invalid selection, not found, or error messages.

- `engine` responsibilities:
  - Request the saved user profiles from storage.
  - Map the user's displayed selection number to the correct stored row.
  - Request deletion from storage only after the user confirms deletion.
  - Return success, cancellation, invalid selection, not found, or error responses to the interface.

- `storage` responsibilities:
  - Retrieve all saved user profiles from the Google Sheet.
  - Include row numbers so the engine can delete the correct row.
  - Delete the requested row from the Google Sheet.
  - Return success, not found, or error responses to the engine.

### Manage Saved Job Analyses Mapping

- `interface` responsibilities:
  - Ask the engine for the saved job analyses.
  - Display a summarized list of saved job analyses.
  - Ask the user to select a job analysis from the displayed list.
  - Display the full selected job analysis.
  - Ask the user to confirm deletion.
  - Display success, cancellation, invalid selection, not found, or error messages.

- `engine` responsibilities:
  - Request the saved job analyses from storage.
  - Map the user's displayed selection number to the correct stored row.
  - Request deletion from storage only after the user confirms deletion.
  - Return success, cancellation, invalid selection, not found, or error responses to the interface.

- `storage` responsibilities:
  - Retrieve all saved job analyses from the Google Sheet.
  - Include row numbers so the engine can delete the correct row.
  - Delete the requested row from the Google Sheet.
  - Return success, not found, or error responses to the engine.

## Part C: Interface Contracts

### Job Description Analysis

#### `interface -> engine`

- Function(s):
  - `analyze_job_description(job_description: str) -> response_payload`
  - `save_existing_job_analysis(analysis_data: dict) -> response_payload`

- Input payload:
  - `{"job_description": str}`
  - `{"analysis_data": {"company_name": str, "job_title": str, "required_skills": list[str], "preferred_skills": list[str], "responsibilities": list[str], "keywords": list[str]}}`

- Return payload/status:
  - `{"status": "success", "data": {"company_name": str, "job_title": str, "required_skills": list[str], "preferred_skills": list[str], "responsibilities": list[str], "keywords": list[str]}}`
  - `{"status": "success", "application_id": int}`
  - `{"status": "error"}`

- Failure statuses:
  - `{"status": "incomplete", "message": "Job description is required."}`
  - `{"status": "invalid_input", "message": "Input does not appear to be a job description."}`
  - `{"status": "ai_error", "message": "Could not analyze job description."}`
  - `{"status": "generation_failed", "message": "Could not understand the job analysis."}`

#### `engine -> storage`

- Function(s):
  - `save_job_analysis(job_analysis: job_analysis_record) -> response_payload`
  - `get_job_analysis(application_id: int | str) -> response_payload`
  - `list_job_analyses() -> response_payload`
  - `delete_job_analysis_by_row(row_number: int) -> response_payload`

- Input payload:
  - `{"company_name": str, "job_title": str, "required_skills": list[str], "keywords": list[str]}`
  - `{"application_id": int | str}`
  - `{}`
  - `{"row_number": int}`

- Return payload/status:
  - `{"status": "success", "application_id": int}`
  - `{"status": "error"}`
  - `{"status": "success", "data": {"application_id": int | str, "company_name": str, "job_title": str, "required_skills": list[str], "keywords": list[str]}}`
  - `{"status": "success", "data": [{"row_number": int, "application_id": int | str, "company_name": str, "job_title": str, "required_skills": list[str], "keywords": list[str]}]}`
  - `{"status": "success", "message": "Job analysis deleted successfully."}`

- Failure statuses:
  - `{"status": "error"}` means required fields were missing or the Google Sheet operation failed.
  - `{"status": "not_found", "message": "Job analysis record was not found."}`

### User Profile Management

#### `interface -> engine`

- Function(s):
  - `save_user_profile(user_profile: dict) -> response_payload`
  - `get_user_profile(user_id: int | str) -> response_payload`

- Input payload:
  - `{"name": str, "email": str, "phone_number": str, "university": str, "degree": str, "skills": list[str], "projects": list[str], "experience": list[str]}`
  - `{"user_id": int | str}`

- Return payload/status:
  - `{"status": "success", "save_status": "success", "user_id": int}`
  - `{"status": "success", "data": {"user_id": int | str, "name": str, "email": str, "phone_number": str, "university": str, "degree": str, "skills": list[str], "projects": list[str], "experience": list[str]}}`

- Failure statuses:
  - `{"status": "incomplete_profile", "message": "User profile is missing required information."}`
  - `{"status": "storage_error", "message": "Could not save user profile."}`
  - `{"status": "not_found", "message": "User profile was not found."}`

#### `engine -> storage`

- Function(s):
  - `save_user_profile(user_profile: user_profile_record) -> response_payload`
  - `get_user_profile(user_id: int | str) -> response_payload`
  - `list_user_profiles() -> response_payload`
  - `delete_user_profile_by_row(row_number: int) -> response_payload`

- Input payload:
  - `{"name": str, "email": str, "phone_number": str, "university": str, "degree": str, "skills": list[str], "projects": list[str], "experience": list[str]}`
  - `{"user_id": int | str}`
  - `{}`
  - `{"row_number": int}`

- Return payload/status:
  - `{"status": "success", "user_id": int}`
  - `{"status": "error"}`
  - `{"status": "success", "data": {"user_id": int | str, "name": str, "email": str, "phone_number": str, "university": str, "degree": str, "skills": list[str], "projects": list[str], "experience": list[str]}}`
  - `{"status": "success", "data": [{"row_number": int, "user_id": int | str, "name": str, "email": str, "phone_number": str, "university": str, "degree": str, "skills": list[str], "projects": list[str], "experience": list[str]}]}`
  - `{"status": "success", "message": "User profile deleted successfully."}`

- Failure statuses:
  - `{"status": "error"}` means required fields were missing or the Google Sheet operation failed.
  - `{"status": "not_found", "message": "User profile was not found."}`

### Resume and Cover Letter Generation

#### `interface -> engine`

- Function(s):
  - `generate_application_materials(user_profile: dict, job_analysis: dict) -> response_payload`
  - `generate_materials_for_saved_records(user_id: int | str, application_id: int | str, save: bool = False) -> response_payload`

- Input payload:
  - `{"user_profile": {"name": str, "email": str, "phone_number": str, "university": str, "degree": str, "skills": list[str], "projects": list[str], "experience": list[str]}, "job_analysis": {"company_name": str, "job_title": str, "required_skills": list[str], "keywords": list[str]}}`
  - `{"user_id": int | str, "application_id": int | str, "save": bool}`

- Return payload/status:
  - `{"status": "success", "data": {"resume": {"skills": list[str], "projects": list[str], "experience": list[str]}, "cover_letter": str, "strengths": list[str], "weaknesses": list[str]}}`
  - `{"status": "success", "data": {"resume": {"skills": list[str], "projects": list[str], "experience": list[str]}, "cover_letter": str, "strengths": list[str], "weaknesses": list[str]}, "save_status": "success" | "exists" | "error"}`

- Failure statuses:
  - `{"status": "incomplete_profile", "message": "User profile is required before generating materials."}`
  - `{"status": "missing_job_analysis", "message": "Job analysis is required before generating materials."}`
  - `{"status": "generation_failed", "message": "Could not understand the generated materials."}`
  - `{"status": "ai_error", "message": "Could not generate application materials."}`

#### `engine -> storage`

- Function(s):
  - `save_generated_materials(materials: generated_materials_record) -> storage_status`
  - `get_generated_materials(application_id: int | str, user_id: int | str | None = None) -> response_payload`

- Input payload:
  - `{"application_id": int | str, "user_id": int | str, "resume_skills": list[str], "resume_projects": list[str], "resume_experience": list[str], "cover_letter": str, "strengths": list[str], "weaknesses": list[str]}`
  - `{"application_id": int | str, "user_id": int | str | None}`

- Return payload/status:
  - `"success"`
  - `"exists"`
  - `"error"`
  - `{"status": "success", "data": {"application_id": int | str, "user_id": int | str, "resume": {"skills": list[str], "projects": list[str], "experience": list[str]}, "cover_letter": str, "strengths": list[str], "weaknesses": list[str]}}`

- Failure statuses:
  - `"exists"` means generated materials for that `application_id` and `user_id` are already stored.
  - `"error"` means required fields were missing or the Google Sheet operation failed.
  - `{"status": "not_found", "message": "Generated materials were not found."}`

#### `interface -> export`

- Function(s):
  - `export_materials_to_docx(materials_data: dict, user_profile: dict, output_dir: str = "outputs", filename: str | None = None) -> str`

- Input payload:
  - `{"materials_data": {"resume": {"skills": list[str], "projects": list[str], "experience": list[str]}, "cover_letter": str, "strengths": list[str], "weaknesses": list[str]}, "user_profile": {"name": str, "email": str, "phone_number": str, "university": str, "degree": str}}`

- Return payload/status:
  - `"outputs/<generated_filename>.docx"`

- Failure statuses:
  - `ValueError` if resume data, cover letter, strengths, weaknesses, or user profile data are missing.
  - `PermissionError` if the file cannot be written because it is open or blocked by the operating system.
  - General export error if the `.docx` file cannot be created.

### Manage Saved User Profiles

#### `interface -> engine`

- Function(s):
  - `list_user_profiles() -> response_payload`
  - `delete_user_profile_by_index(entry_number: int) -> response_payload`

- Input payload:
  - `{}`
  - `{"entry_number": int}`

- Return payload/status:
  - `{"status": "success", "data": [{"row_number": int, "user_id": int | str, "name": str, "email": str, "phone_number": str, "university": str, "degree": str, "skills": list[str], "projects": list[str], "experience": list[str]}]}`
  - `{"status": "success", "message": "User profile deleted successfully."}`

- Failure statuses:
  - `{"status": "not_found", "message": "No user profiles were found."}`
  - `{"status": "invalid_selection", "message": "Please choose a valid entry number."}`
  - `{"status": "error", "message": "Could not delete user profile."}`

#### `engine -> storage`

- Function(s):
  - `list_user_profiles() -> response_payload`
  - `delete_user_profile_by_row(row_number: int) -> response_payload`

- Input payload:
  - `{}`
  - `{"row_number": int}`

- Return payload/status:
  - `{"status": "success", "data": [{"row_number": int, "user_id": int | str, "name": str, "email": str, "phone_number": str, "university": str, "degree": str, "skills": list[str], "projects": list[str], "experience": list[str]}]}`
  - `{"status": "success", "message": "User profile deleted successfully."}`

- Failure statuses:
  - `{"status": "not_found", "message": "No user profiles were found."}`
  - `{"status": "error", "message": "Could not delete user profile."}`

### Manage Saved Job Analyses

#### `interface -> engine`

- Function(s):
  - `list_job_analyses() -> response_payload`
  - `delete_job_analysis_by_index(entry_number: int) -> response_payload`

- Input payload:
  - `{}`
  - `{"entry_number": int}`

- Return payload/status:
  - `{"status": "success", "data": [{"row_number": int, "application_id": int | str, "company_name": str, "job_title": str, "required_skills": list[str], "keywords": list[str]}]}`
  - `{"status": "success", "message": "Job analysis deleted successfully."}`

- Failure statuses:
  - `{"status": "not_found", "message": "No job analyses were found."}`
  - `{"status": "invalid_selection", "message": "Please choose a valid entry number."}`
  - `{"status": "error", "message": "Could not delete job analysis."}`

#### `engine -> storage`

- Function(s):
  - `list_job_analyses() -> response_payload`
  - `delete_job_analysis_by_row(row_number: int) -> response_payload`

- Input payload:
  - `{}`
  - `{"row_number": int}`

- Return payload/status:
  - `{"status": "success", "data": [{"row_number": int, "application_id": int | str, "company_name": str, "job_title": str, "required_skills": list[str], "keywords": list[str]}]}`
  - `{"status": "success", "message": "Job analysis deleted successfully."}`

- Failure statuses:
  - `{"status": "not_found", "message": "No job analyses were found."}`
  - `{"status": "error", "message": "Could not delete job analysis."}`
