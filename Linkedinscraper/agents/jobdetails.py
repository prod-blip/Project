# File: agents/jobdetails.py

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv
import requests
import os
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "linkedin-data-api.p.rapidapi.com"

URL = "https://linkedin-data-api.p.rapidapi.com/get-job-details"

def get_job_details(job_id: str) -> Dict[str, Any] | None:
    """
    Get detailed information about a specific LinkedIn job based on its ID.
    """
    params = {
        "id": job_id
    }
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    try:
        response = requests.get(
            URL,
            headers=headers,
            params=params,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching job details for ID {job_id}: {str(e)}")
        return None

class Skill(BaseModel):
    """Model representing a required skill for a job."""
    name: str = Field(description="Name of the skill")
    level: Optional[str] = Field(description="Required proficiency level", default=None)

class JobDetail(BaseModel):
    """Model to represent detailed information about a job."""
    job_id: str = Field(description="The job ID")
    title: str = Field(description="The job title")
    company: str = Field(description="The company name")
    location: str = Field(description="Job location")
    description: str = Field(description="Job description")
    required_skills: List[Skill] = Field(description="Required skills for the job")
    experience_level: str = Field(description="Required experience level")
    job_type: str = Field(description="Type of job (full-time, part-time, etc.)")

model = OpenAIModel("gpt-4o-mini")

system_prompt = """You are an assistant that analyzes LinkedIn job details.

When given detailed information about a job posting, extract the key information including:
- Job title
- Company name
- Location
- Job description summary
- Required skills
- Experience level
- Job type

Structure this information clearly so it can be used for job matching or analysis.
"""

job_details_agent = Agent(
    model=model,
    system_prompt=system_prompt,
    result_type=JobDetail,
)

@job_details_agent.tool
def job_details_tool(context: RunContext[Any], job_id: str) -> Dict[str, Any] | None:
    """
    Get detailed information about a LinkedIn job based on its ID.
    """
    return get_job_details(job_id)

# def get_details_for_job(job_id: str) -> JobDetail:
#     """
#     Helper function to get details for a specific job ID.
#     """
#     result = job_details_agent.run_sync(f"Analyze job details for job ID: {job_id}")
#     return result.data

result = job_details_agent.run_sync("please fetch job id for '4198449849' id")
print(result.data)