
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Any, Dict, List
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv
import requests
import os
load_dotenv()

model = OpenAIModel("gpt-4o-mini")

system_prompt = """You are an assistant that compares the job details of the LinkedIn job postings with my resume pointers. Basis the comparison, you will provide me with the following:
1. A confidence score (0-100) for each job posting based on how well it matches my resume.
2. A summary of the job posting.
3. A list of required skills and experience levels for each job posting.

My resume pointers are:
- 5+ years of experience in Product Management
- Strong analytical skills
- Proficient in Python and SQL
- Experience with Agile methodologies
- Excellent communication and leadership skills
- Familiarity with data analysis tools
- Experience in the tech industry
- Strong problem-solving skills
- Ability to work in a fast-paced environment
- Experience with cross-functional teams
- Strong understanding of user experience design
- Experience with A/B testing and user research
- Familiarity with project management tools
- Strong understanding of market research and competitive analysis
- Experience with product roadmapping and prioritization
"""

class JobAnalyser(BaseModel):
    
    score: int = Field(description="The confidence score (0-100) for the job posting")
    summary: str = Field(description="A summary of the job posting")
    required_skills: List[str] = Field(description="List of required skills for the job")
    

job_analyser_agent = Agent(
    model=model,
    system_prompt=system_prompt,
    result_type=List[JobAnalyser],
)