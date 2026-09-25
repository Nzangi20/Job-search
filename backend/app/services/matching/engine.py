from app.models import CandidateProfile, Job


def _norm_list(items: list | None) -> set[str]:
    return {str(i).strip().lower() for i in (items or []) if str(i).strip()}


def build_candidate_dict(profile: CandidateProfile) -> dict:
    data = profile.structured_data or {}
    skills = _norm_list([s.skill.name for s in profile.skills] if profile.skills else [])
    if data.get("skills"):
        skills |= _norm_list(data.get("skills"))
    return {
        "skills": list(skills),
        "preferred_roles": profile.preferred_roles or data.get("potential_job_titles") or [],
        "preferred_locations": profile.preferred_locations or [],
        "employment_types": profile.employment_types or [],
        "experience_level": profile.experience_level or data.get("seniority_level"),
        "education": data.get("education") or [],
        "programming_languages": data.get("programming_languages") or [],
        "frameworks": data.get("frameworks") or [],
        "tools": data.get("tools") or [],
    }


def _overlap_score(required: set[str], candidate: set[str]) -> float:
    if not required:
        return 0.85
    if not candidate:
        return 0.0
    hit = len(required & candidate)
    return hit / len(required)


def compute_match_scores(
    candidate: dict,
    job: Job,
    analysis: dict,
    profile: CandidateProfile,
) -> tuple[dict[str, float], list[str], list[str]]:
    c_skills = _norm_list(candidate.get("skills"))
    c_skills |= _norm_list(candidate.get("programming_languages"))
    c_skills |= _norm_list(candidate.get("frameworks"))
    c_skills |= _norm_list(candidate.get("tools"))

    required = _norm_list(analysis.get("required_skills"))
    preferred = _norm_list(analysis.get("preferred_skills"))
    all_job_skills = required | preferred

    skills_score = _overlap_score(required, c_skills)
    if preferred:
        skills_score = 0.7 * skills_score + 0.3 * _overlap_score(preferred, c_skills)

    exp_text = (analysis.get("experience_requirement") or job.experience_required or "").lower()
    cand_exp = (candidate.get("experience_level") or "").lower()
    exp_score = 0.7
    if "senior" in exp_text and "junior" in cand_exp:
        exp_score = 0.4
    elif "junior" in exp_text or "entry" in exp_text:
        exp_score = 0.9 if "junior" in cand_exp or "entry" in cand_exp else 0.6

    roles = _norm_list(candidate.get("preferred_roles"))
    title = job.title.lower()
    role_score = 0.5
    if roles:
        role_score = max((0.95 if r in title else 0.4 for r in roles), default=0.5)

    loc_prefs = _norm_list(candidate.get("preferred_locations"))
    loc_text = (job.location or analysis.get("location") or "").lower()
    loc_score = 0.6
    if job.remote or analysis.get("remote_status"):
        loc_score = 0.95 if any(p in {"remote", "worldwide"} for p in loc_prefs) else 0.75
    elif loc_prefs:
        loc_score = 0.95 if any(p in loc_text for p in loc_prefs) else 0.45

    edu_score = 0.8
    if analysis.get("education_requirement"):
        edu_score = 0.7

    tech = _norm_list(candidate.get("programming_languages")) | _norm_list(candidate.get("frameworks"))
    tech_score = _overlap_score(all_job_skills, tech) if all_job_skills else 0.75

    pref_score = 0.7
    if profile.employment_types and job.employment_type:
        pref_score = (
            0.95
            if job.employment_type.lower() in _norm_list(profile.employment_types)
            else 0.5
        )

    scores = {
        "skills": min(1.0, skills_score),
        "experience": exp_score,
        "role": role_score,
        "location": loc_score,
        "education": edu_score,
        "technology": min(1.0, tech_score),
        "preference": pref_score,
    }

    reasons = []
    gaps = []
    
    # Skills matching & gaps
    for s in required:
        if s in c_skills:
            reasons.append(f"You have {s.title()} experience")
        else:
            gaps.append(f"{s.title()} is listed as a required skill but is not present in your CV")
            
    for s in preferred:
        if s in c_skills:
            reasons.append(f"You have preferred skill: {s.title()}")
        else:
            gaps.append(f"{s.title()} is listed as a preferred skill but is not present in your CV")

    # Experience alignment
    if exp_score >= 0.8:
        reasons.append("Your experience level aligns with the requirement")
    elif exp_score < 0.6:
        gaps.append(f"The position asks for {exp_text or 'more experience'} than indicated in your profile")

    # Location & Remote
    if job.remote or analysis.get("remote_status"):
        reasons.append("The job accepts remote applicants")
    elif loc_prefs and any(p in loc_text for p in loc_prefs):
        reasons.append(f"Job location ({job.location}) matches your location preferences")
    elif loc_prefs:
        gaps.append(f"Job location ({job.location or 'On-site'}) may not align with your location preferences")

    # Role matching
    if role_score >= 0.9:
        reasons.append("Your preferred roles match this position's title")

    # Employment preference
    if pref_score >= 0.9:
        reasons.append(f"Matches your preferred employment type ({job.employment_type})")

    # De-duplicate reasons & gaps preserving order
    def _dedup_list(lst: list[str]) -> list[str]:
        seen = set()
        res = []
        for x in lst:
            if x not in seen:
                seen.add(x)
                res.append(x)
        return res

    return scores, _dedup_list(reasons)[:10], _dedup_list(gaps)[:10]
