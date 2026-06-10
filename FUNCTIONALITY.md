# FUNCTIONALITY.md

## Purpose

Define what the system should do, i.e., functionalities.

### Functionality 1: Job Description Analysis

- Input:
  - Job description with responsibilities, required skills, preferred skills, job title, and company information.

- Output:
  - Structured summary of the job, including company name, job title, required skills, preferred skills, responsibilities, and keywords.
  - If the user chooses to save the analysis, the system also returns an automatically generated `application_id` internally.

- Success:
  - The system extracts the main job requirements and displays them in organized sections.
  - If saving is requested, the system saves the analyzed job description in Google Sheets and stores the generated `application_id`.
  - The saved job analysis can later be selected from a list when generating application materials.

- Failure/Edge Cases:
  - Empty job description -> return `incomplete` and ask the user to enter a job description.
  - Gemini API error -> return `ai_error` and ask the user to try again.
  - Job description does not describe a job -> return `invalid_input`.
  - Storage error while saving the job analysis -> return save status `error`.

### Functionality 2: User Profile Management

- Input:
  - User profile information, including name, email, phone number, university, degree, skills, projects, and experience.

- Output:
  - Structured user profile data that can be saved and later used for resume and cover letter generation.
  - If the profile is saved successfully, the system returns an automatically generated `user_id` internally.

- Success:
  - The system validates the required user profile fields and saves the profile for later use.
  - The saved user profile can later be selected from a list when generating application materials.
  - The system stores skills, projects, and experience as structured lists.

- Failure/Edge Cases:
  - Missing required profile information -> return `incomplete_profile`.
  - Storage error while saving the profile -> return `storage_error`.
  - Requested user profile does not exist -> return `not_found`.

### Functionality 3: Resume and Cover Letter Generation

- Input:
  - Saved user profile selected by the user.
  - Saved job analysis selected by the user.
  - The system retrieves the saved user profile and saved job analysis from Google Sheets.

- Output:
  - Tailored resume content separated into skills, projects, and experience sections.
  - A cover letter draft.
  - Strengths that explain how the user can use their best matches for the job.
  - Weaknesses that explain how the user can prepare for missing or weaker job requirements before an interview or assessment.
  - If requested, a saved `.docx` file containing the resume, cover letter, strengths, and weaknesses.

- Success:
  - The system generates resume content and a cover letter that match the user’s real background with the job requirements.
  - The system does not invent skills, projects, education, experience, or achievements.
  - If saving is requested, the generated materials are saved in Google Sheets.
  - If document export is requested, the generated materials are exported to a `.docx` file in the `outputs/` folder.
  - The exported `.docx` file includes formatted resume sections, separator lines, a cover letter page, and a strengths and weaknesses page.

- Failure/Edge Cases:
  - Missing user profile information -> return `incomplete_profile`.
  - Missing job analysis -> return `missing_job_analysis`.
  - Gemini API error -> return `ai_error`.
  - Generated response is empty or badly formatted -> return `generation_failed`.
  - Document export error -> display an export error message and avoid crashing the program.
  - Missing user ID or application ID from a selected record -> return `invalid_selection`.

### Functionality 4: Manage Saved User Profiles

- Input:
  - User chooses the manage users option.
  - User selects a saved user profile from a displayed list.
  - User confirms whether to delete the selected profile.

- Output:
  - A summarized list of saved user profiles.
  - Full details for the selected user profile.
  - A success or cancellation message after the delete confirmation.

- Success:
  - The system displays saved user profiles using a readable summary.
  - The system displays the full selected user profile before deletion.
  - If deletion is confirmed, the selected user profile is removed from Google Sheets.
  - If deletion is not confirmed, the profile remains saved.

- Failure/Edge Cases:
  - No saved user profiles exist -> return `not_found`.
  - Invalid selection -> return `invalid_selection`.
  - User chooses to go back -> return `cancelled`.
  - Storage error while deleting -> return `error`.

### Functionality 5: Manage Saved Job Analyses

- Input:
  - User chooses the manage jobs option.
  - User selects a saved job analysis from a displayed list.
  - User confirms whether to delete the selected job analysis.

- Output:
  - A summarized list of saved job analyses.
  - Full details for the selected job analysis.
  - A success or cancellation message after the delete confirmation.

- Success:
  - The system displays saved job analyses using a readable summary.
  - The system displays the full selected job analysis before deletion.
  - If deletion is confirmed, the selected job analysis is removed from Google Sheets.
  - If deletion is not confirmed, the job analysis remains saved.

- Failure/Edge Cases:
  - No saved job analyses exist -> return `not_found`.
  - Invalid selection -> return `invalid_selection`.
  - User chooses to go back -> return `cancelled`.
  - Storage error while deleting -> return `error`.
