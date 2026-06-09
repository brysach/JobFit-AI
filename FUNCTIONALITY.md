# FUNCTIONALITY.md

## Purpose

Define what the system should do, i.e., functionalities.

### Functionality 1: Job Description Analysis

- Input:
  - Job description with responsibilities, required skills, preferred skills, and company information.

- Output:
  - Structured summary of the job, including job title, required skills, preferred skills, responsibilities, and keywords.
  - If the user chooses to save the analysis, the system also returns an automatically generated `application_id`.

- Success:
  - The system extracts the main job requirements and displays them in organized sections.
  - If saving is requested, the system saves the analyzed job description in Google Sheets and displays the generated `application_id`.

- Failure/Edge Cases:
  - Empty job description -> return `incomplete` and ask the user to enter a job description.
  - Gemini API error -> return `ai_error` and ask the user to try again.
  - Job description does not describe a job -> return `invalid_input`.
  - Storage error while saving the job analysis -> return save status `error`.

### Functionality 2: User Profile Management

- Input:
  - User profile information, including name, education, skills, projects, work experience, and leadership experience.

- Output:
  - Structured user profile data that can be saved and later used for resume and cover letter generation.
  - If the profile is saved successfully, the system returns an automatically generated `user_id`.

- Success:
  - The system validates the required user profile fields and saves the profile for later use.
  - The system displays the generated `user_id` so the user can use it later to generate application materials.

- Failure/Edge Cases:
  - Missing required profile information -> return `incomplete_profile`.
  - Storage error while saving the profile -> return `storage_error`.
  - Requested user profile does not exist -> return `not_found`.

### Functionality 3: Resume and Cover Letter Generation

- Input:
  - Saved `user_id`.
  - Saved `application_id`.
  - The system retrieves the saved user profile and saved job analysis from Google Sheets.

- Output:
  - Tailored resume bullet suggestions.
  - A cover letter draft.
  - Warnings about job requirements that are weakly supported or missing from the user profile.
  - If requested, a saved `.docx` file containing the generated resume bullets and cover letter.

- Success:
  - The system generates resume bullets and a cover letter that match the user’s real background with the job requirements.
  - If saving is requested, the generated materials are saved in Google Sheets.
  - If document export is requested, the generated materials are exported to a `.docx` file in the `outputs/` folder.

- Failure/Edge Cases:
  - Missing user profile information -> return `incomplete_profile`.
  - Missing job analysis -> return `missing_job_analysis`.
  - Gemini API error -> return `ai_error`.
  - Generated response is empty or badly formatted -> return `generation_failed`.
  - Document export error -> display an export error message and avoid crashing the program.
