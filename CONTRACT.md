# CONTRACT.md (Short Teaching Template)

## Purpose

Use this file to map each functionality to component ownership and explicit interfaces.

## Part B: Architecture Mapping

For each functionality, map responsibilities to components.

### Job Description Analysis Mapping

- `interface` responsibilities:
  - Collect the pasted job description from the user.
  - Send the job description to the engine.
  - Display the extracted job title, skills, responsibilities, and keywords.
- `engine` responsibilities:
  - Validate that the job description is not empty.
  - Send the job description to Gemini API.
  - Parse Gemini’s response into structured data.
  - Return success or failure status to the interface.
- `storage` responsibilities:
  - Save the analyzed job description if the user chooses to save the application.
  - Retrieve previous job analysis data when needed.

### Resume and Cover Letter Generation Mapping

- `interface` responsibilities:
  - Show the generated resume bullets and cover letter.
  - Allow the user to copy or edit the generated content.
  - Display errors when required information is missing.
- `engine` responsibilities:
  - Validate the user profile and job analysis.
  - Use Gemini API to generate resume bullets and a cover letter.
  - Ensure the generated content only uses information provided by the user.
  - Return structured generated content to the interface.
- `storage` responsibilities:
  - Save generated resume bullets and cover letter if the user saves the application.
  - Retrieve saved generated content for a previous application.

## Part C: Interface Contracts

### Job Description Analysis

### `interface -> engine`

- Function(s):
  - `analyze_job_description(job_description: str) -> response_payload`
- Input payload:
  - `{"job_description": str}`
- Return payload/status:
  - `{"status": "success", "data": {"job_title": str, "required_skills": list[str], "preferred_skills": list[str], "responsibilities": list[str], "keywords": list[str]}}`
- Failure statuses:
  - `{"status": "incomplete", "message": "Job description is required."}`
  - `{"status": "invalid_input", "message": "Input does not appear to be a job description."}`
  - `{"status": "ai_error", "message": "Could not analyze job description."}`

### `engine -> storage`

- Function(s):
  - `save_job_analysis(job_analysis: job_analysis_record) -> response_payload`
  - `get_job_analysis(application_id: str) -> response_payload`
- Input payload:
  - `{"application_id": int, "job_title": str, "required_skills": list[str], "keywords": list[str]}`
- Return payload/status:
  - `{"status": "success", "id": int}`
- Failure statuses:
  - `{"status": "storage_error", "message": "Could not save job analysis."}`
  - `{"status": "not_found", "message": "Job analysis record was not found."}`

### Resume and Cover Letter Generation

#### `interface -> engine`

- Function(s):
  - `generate_application_materials(user_profile: dict, job_analysis: dict) -> response_payload`
- Input payload:
  - `{"user_profile": {"education": str, "skills": list[str], "projects": list[str], "experience": list[str]}, "job_analysis": {"job_title": str, "required_skills": list[str], "keywords": list[str]}}`
- Return payload/status:
  - `{"status": "success", "data": {"resume_bullets": list[str], "warnings": list[str]}}`
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
  - `{"application_id": int, "resume_bullets": list[str], "cover_letter": str}`
- Return payload/status:
  - Success:
    - `{"status": "success", "id": int}`
- Failure statuses:
  - `{"status": "storage_error", "message": "Could not save generated materials."}`
  - `{"status": "not_found", "message": "Generated materials were not found."}`
