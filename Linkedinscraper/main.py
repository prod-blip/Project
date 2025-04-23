# File: main.py

from typing import TypedDict, List, Dict, Any, Optional
from agents.jobextractor import get_job_ids_for_keyword, JobSearchId
from agents.jobdetails import get_details_for_job, JobDetail
from langgraph.graph import StateGraph, START, END
import asyncio


class AgentState(TypedDict):
    """State passed between the agents in the workflow."""
    search_keyword: str
    job_ids: Optional[List[JobSearchId]]
    job_details: Optional[List[JobDetail]]
    status: str
    error: Optional[str]


def extract(state: AgentState) -> AgentState:
    """Extract job IDs for the provided search keyword."""
    
        # Get the search keyword from the state
    keyword = state["search_keyword"]
        
        # Get job IDs for the keyword
    job_ids = get_job_ids_for_keyword(keyword)
        
        
        


async def details(state: AgentState) -> AgentState:
    """Get detailed information for each job ID."""
    try:
        # Get the job IDs from the state
        job_ids = state.get("job_ids", [])
        
        if not job_ids:
            return {
                **state,
                "status": "error",
                "error": "No job IDs available to fetch details"
            }
        
        # Get details for each job ID
        job_details = []
        for job_id_obj in job_ids[:5]:  # Limit to first 5 to avoid rate limits
            job_detail = get_details_for_job(job_id_obj.job_id)
            job_details.append(job_detail)
            await asyncio.sleep(1)  # Add delay to avoid API rate limits
        
        # Update the state with the job details
        return {
            **state,
            "job_details": job_details,
            "status": "completed"
        }
    except Exception as e:
        return {
            **state,
            "status": "error",
            "error": f"Error fetching job details: {str(e)}"
        }


def should_continue(state: AgentState) -> str:
    """Determine whether to continue to the next step or end due to an error."""
    if state.get("status") == "error":
        return END
    return "Job Details Agent"


# Build the workflow graph
builder = StateGraph(AgentState)

# Add nodes
builder.add_node("Job Extractor Agent", extract)
builder.add_node("Job Details Agent", details)

# Add edges with conditional routing
builder.add_edge(START, "Job Extractor Agent")
builder.add_conditional_edges(
    "Job Extractor Agent",
    should_continue,  # This is the routing function that returns a node name
    {
        END: END,  # If should_continue returns END, route to END
        "Job Details Agent": "Job Details Agent"  # If should_continue returns "Job Details Agent", route to that node
    }
)
builder.add_edge("Job Details Agent", END)

# Compile the graph
workflow = builder.compile()


async def run_workflow(search_keyword: str):
    """Run the complete workflow with the provided search keyword."""
    initial_state = AgentState(
        search_keyword=search_keyword,
        job_ids=None,
        job_details=None,
        status="starting",
        error=None
    )
    
    # Execute the workflow
    result = await workflow.ainvoke(initial_state)
    
    # Process and return the results
    if result["status"] == "error":
        print(f"Workflow failed: {result['error']}")
        return None
    
    print(f"Successfully processed {len(result['job_details'])} job listings for '{search_keyword}'")
    return result["job_details"]


# Example usage
if __name__ == "__main__":
    async def main():
        await run_workflow("product manager")
    
    asyncio.run(main())