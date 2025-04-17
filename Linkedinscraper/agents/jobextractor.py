# File: agents/jobextractor.py

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Any, Dict, List
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv
import requests
import os
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "linkedin-data-api.p.rapidapi.com"

URL = "https://linkedin-data-api.p.rapidapi.com/search-jobs-v2"

def search_linkedin_jobs(keyword: str) -> Dict[str, Any] | None:
    """
    Search for jobs on LinkedIn based on a keyword.
    """
    params = {
        "keywords": keyword,
        "locationId": "92000000",
        "datePosted": "anyTime",
        "sort": "mostRelevant"
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
        print(f"Error fetching LinkedIn job data: {str(e)}")
        return None

class JobSearchId(BaseModel):
    """Model to represent a job ID from search results."""
    job_id: str = Field(description="The job ID from LinkedIn")
    title: str = Field(description="The job title")
    company: str = Field(description="The company name")

model = OpenAIModel("gpt-4o-mini")

system_prompt = """You are an assistant that extracts job IDs from LinkedIn job search results.

When given search results for jobs, extract the job IDs along with their titles and company names.
The job IDs are needed to fetch detailed information about each job posting.

IMPORTANT: Return ONLY the job IDs, titles, and company names as structured data.
"""

job_search_agent = Agent(
    model=model,
    system_prompt=system_prompt,
    result_type=List[JobSearchId],
)

@job_search_agent.tool
def search_linkedin_jobs_tool(context: RunContext[Any], keyword: str) -> Dict[str, Any] | None:
    """
    Search for LinkedIn job listings based on a keyword or job title.
    Return the raw search results which contain job IDs.
    """
    return search_linkedin_jobs(keyword)

def get_job_ids_for_keyword(keyword: str) -> List[JobSearchId]:
    """
    Helper function to get job IDs for a specific keyword.
    """
    result = job_search_agent.run_sync(f"Extract job IDs for '{keyword}' jobs")
    return result.data