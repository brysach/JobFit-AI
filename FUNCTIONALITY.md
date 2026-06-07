# FUNCTIONALITY.md

## Purpose

Define what the system should do, i.e., functionalities.

### Functionality 1: Job Description Analysis

- Input:
  - Job description with responsibilities, required skills, preferred skills, and company information.
- Output:
  - Structured summary of the job, including job title, required skills, preferred skills, responsibilities, keywords, and missing information.
- Success:
  - The system extracts the main job requirements and displays them in organized sections.
- Failure/Edge Cases:
  - Empty job description -> return `incomplete` and ask the user to enter a job description.
  - Gemini API error -> return `ai_error` and ask the user to try again.
  - Job description does not describe a job -> return `invalid_input`.

### Functionality 2: User Profile Management

- Input:
  - User profile information, including name, education, skills, projects, work experience, and leadership experience.
- Output:
  - Structured user profile data that can be saved and later used for resume and cover letter generation.
- Success:
  - The system validates the required user profile fields and saves the profile for later use.
- Failure/Edge Cases:
  - Missing required profile information -> return `incomplete_profile`.
  - User profile already exists -> return `exists`.
  - Storage error while saving the profile -> return `storage_error`.
  - Requested user profile does not exist -> return `not_found`.

### Functionality 3: Resume and Cover Letter Generation

- Input:
  - User profile with name, education, skills, projects, work experience, leadership experience, and the analyzed job description.
- Output:
  - Tailored resume bullet suggestions and a cover letter draft.
- Success:
  - The system generates resume bullets and a cover letter that match the user’s real background with the job requirements.
- Failure/Edge Cases:
  - Missing user profile information -> return `incomplete_profile`.
  - Missing job analysis -> return `missing_job_analysis`.
  - Gemini API error -> return `ai_error`.
  - Generated response is empty or badly formatted -> return `generation_failed`.
