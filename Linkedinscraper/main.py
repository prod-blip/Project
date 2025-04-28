# File: main.py

from typing import TypedDict, List, Dict, Any, Optional
from agents.jobextractor import search_linkedin_jobs, JobSearchId, job_search_agent
from agents.jobdetails import get_job_details, JobDetail, job_details_agent
from agents.jobanalyser import job_analyser_agent
from langgraph.graph import StateGraph, START, END
import asyncio


class AgentState(TypedDict):
    """State passed between the agents in the workflow."""
    search_keyword: str
    job_ids: Optional[List[JobSearchId]]
    job_details: Optional[List[JobDetail]]
    job_scores: Optional[List[Any]]
    status: str
    error: Optional[str]


async def extract(state: AgentState) -> AgentState:
    """Extract job IDs for the provided search keyword."""
    job_info = await job_search_agent.run(state["search_keyword"])
    
    # print("Type of job_info:", type(job_info))   
    # print("job_info:", job_info)

    job_ids = [job.job_id for job in job_info.data]

    job_ids = job_ids[:2]
    print("job_ids:", job_ids)

    return {**state, "job_ids": job_ids, "status": "job_ids_extracted"}
    


async def details(state: AgentState) -> AgentState:
    """Get detailed information for each job ID."""
    job_descriptions = []
    for job in state["job_ids"]:
        # job_id = job.job_id
        detail = await job_details_agent.run(job)
        print("Job Description:", detail.data.description)
        job_descriptions.append(detail.data.description)
    
    return {**state, "job_details": job_descriptions, "status": "completed"}

async def analyze(state: AgentState) -> AgentState:
    """Analyze the job details."""
    job_scores = []
    for job in state["job_details"]:

        jobanalysis= await job_analyser_agent.run(job)
        print("Job Score:", jobanalysis.data[0].score)
        job_scores.append(jobanalysis.data[0].score)
    return {**state, "job_scores": job_scores, "status": "analysis_completed"}






# Build the workflow graph
builder = StateGraph(AgentState)

# Add nodes
builder.add_node("Job Extractor Agent", extract)
builder.add_node("Job Details Agent", details)
builder.add_node("Job Analyser Agent", analyze)

# Add edges with conditional routing
builder.add_edge(START, "Job Extractor Agent")
builder.add_edge("Job Extractor Agent", "Job Details Agent")
builder.add_edge("Job Details Agent", "Job Analyser Agent")
builder.add_edge("Job Analyser Agent", END)


# Compile the graph
workflow = builder.compile()


initial_state = AgentState(
    search_keyword="please fetch job id for 'product manager' keyword",
    job_ids=None,
    job_details=None,
    job_scores=None,
    status="started",
    error=None
)
async def main():
    result = await workflow.ainvoke(initial_state)
    # print(result)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())