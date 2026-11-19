"""Structured data extracted from job descriptions and resumes.

The same models are used as the Gemini response schema and as the output of the
rule-based fallback, so downstream matching never cares which extractor ran.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

EduLevel = Literal["none", "diploma", "bachelor", "master", "phd"]
EDU_RANK = {"none": 0, "diploma": 1, "bachelor": 2, "master": 3, "phd": 4}


class SkillReq(BaseModel):
    name: str = Field(description="One atomic skill, e.g. 'Spring Boot'")
    alternatives: list[str] = Field(default_factory=list,
                                    description="Acceptable substitutes stated in the JD, e.g. for "
                                                "'PostgreSQL or MySQL' name='PostgreSQL', alternatives=['MySQL']")
    core: bool = Field(False, description="True for the 2-4 skills that define the role "
                                          "(e.g. in the job title or repeated throughout the JD)")


class JDData(BaseModel):
    title: str = ""
    summary: str = Field("", description="1-2 sentence summary of the role")
    required_skills: list[SkillReq] = Field(default_factory=list)
    preferred_skills: list[SkillReq] = Field(default_factory=list)
    min_years: Optional[float] = Field(None, description="Minimum years of experience required, null if not stated")
    education_level: EduLevel = "none"
    education_required: bool = Field(False, description="True if the degree is a hard requirement")
    education_fields: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list, description="Key duties, one per item")
    other_qualifications: list[str] = Field(default_factory=list,
                                            description="Domain experience, soft skills, certifications")


class Experience(BaseModel):
    title: str = ""
    company: str = ""
    start: Optional[str] = Field(None, description="YYYY-MM (use -01 if only the year is known)")
    end: Optional[str] = Field(None, description="YYYY-MM, or 'present' for a current role")
    description: str = ""


class Education(BaseModel):
    degree: str = ""
    field: str = ""
    institution: str = ""
    end_year: Optional[int] = None
    level: EduLevel = "none"


class Project(BaseModel):
    name: str = ""
    description: str = ""


class ResumeData(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    skills: list[str] = Field(default_factory=list, description="Atomic skills, tools and technologies")
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    # computed after extraction (not asked from the LLM)
    total_years: float = 0.0
