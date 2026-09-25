CV_ANALYSIS = """Analyze the following CV (from ANY industry or job category, e.g., Tech, Marketing, Sales, Finance, HR, Design, Operations, Customer Support, Healthcare, Legal, Administration, Writing, Education) and return structured JSON containing:

- professional_summary (string)
- skills (array of strings — key domain skills, soft skills, technical skills, or operational capabilities)
- programming_languages (array of strings — if applicable, otherwise empty array)
- frameworks (array of strings — if applicable, otherwise empty array)
- tools (array of strings — software, platforms, or tools used, e.g. Excel, Salesforce, Hubspot, Figma, Jira, Python, QuickBooks)
- databases (array of strings — if applicable, otherwise empty array)
- education (array of objects with degree, institution, year if present)
- certifications (array of strings)
- experience (array of objects with title, company, duration, highlights)
- projects (array of objects with name, description)
- potential_job_titles (array of strings — 4 to 8 realistic target job titles across their field)
- seniority_level (string — e.g. Entry Level, Junior, Mid Level, Senior, Lead, Executive)
- personal_info (object with name, email, phone, location ONLY if explicitly in CV)

Do not invent information that is not present in the CV.
Return ONLY valid JSON, no markdown."""

JOB_ANALYSIS = """Analyze this job description and return structured JSON containing:

- required_skills (array of strings)
- preferred_skills (array of strings)
- experience_requirement (string)
- education_requirement (string)
- seniority (string)
- location (string)
- remote_status (boolean)
- employment_type (string)
- salary (object with min, max, currency — only if stated)
- responsibilities (array of strings)
- application_deadline (string or null)

Do not infer requirements that are not supported by the job description.
Return ONLY valid JSON, no markdown."""

MATCH_COMPARISON = """Compare the candidate profile against the job requirements.

Identify:

1. matching_skills (array of strings)
2. missing_required_skills (array of strings)
3. matching_experience (array of strings describing matches)
4. experience_gaps (array of strings)
5. role_compatibility (string: high/medium/low)
6. location_compatibility (string: high/medium/low)
7. education_compatibility (string: high/medium/low)
8. match_highlights (array of short bullet strings for UI, prefix positive with reason)
9. gap_highlights (array of short bullet strings for UI, note missing items)

Do not invent qualifications.
Return ONLY valid JSON, no markdown."""

COVER_LETTER = """Write a tailored cover letter based on the candidate CV and job description.
Be professional, specific, and honest. Do not invent experience.
Return plain text only."""

APPLICATION_ANSWERS = """Answer the application questions using only information from the candidate CV.
If information is missing, say the candidate should address it honestly.
Return JSON array of objects: question, suggested_answer."""

JOB_QUESTION_ANSWER = """You are an expert career consultant, hiring expert, and AI job assistant.
Answer the user's question about the job posting using the candidate's CV and the job description provided.
Provide clear, actionable, concise, and specific guidance based on the candidate's actual qualifications and the employer's requirements.
Format your answer clearly with Markdown bullet points or paragraphs."""

