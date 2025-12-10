"""
SOP Tools for the Dynamic SOP Agent
Tools for retrieving, applying, and managing SOPs
"""

from typing import List, Optional
from ..sop_models import SOPContext, SOPExecution
from ..context_analyzer import ContextAnalyzer
from ..sop_loader import SOPLoader
from datetime import datetime


# Global instances (will be initialized by agent)
sop_loader: Optional[SOPLoader] = None
context_analyzer: Optional[ContextAnalyzer] = None
active_execution: Optional[SOPExecution] = None


def initialize_sop_tools(loader: SOPLoader, analyzer: ContextAnalyzer):
    """Initialize the SOP tools with loader and analyzer instances"""
    global sop_loader, context_analyzer
    sop_loader = loader
    context_analyzer = analyzer


def search_sops_by_context(query: str) -> str:
    """
    Search for relevant SOPs based on user query context.
    Analyzes the query to understand what SOPs would be most relevant.
    
    Args:
        query: User's natural language query describing their need
        
    Returns:
        String describing relevant SOPs with relevance scores
    """
    if not sop_loader or not context_analyzer:
        return "Error: SOP tools not initialized"
    
    # Analyze the query to extract context
    context = context_analyzer.analyze(query)
    
    # Get context summary
    context_summary = context_analyzer.get_context_summary(context)
    
    # Search all repositories for matching SOPs
    all_matches = []
    for repo in sop_loader.repositories.values():
        matches = repo.find_sops_by_context(context)
        all_matches.extend(matches)
    
    # Sort by relevance score
    all_matches.sort(key=lambda x: x[1], reverse=True)
    
    if not all_matches:
        return f"""🔍 No SOPs found matching your query: '{query}'

Detected context:
{context_summary}

Try being more specific or use different keywords."""
    
    # Format results
    result = [f"🎯 Relevant SOPs for: '{query}'\n"]
    result.append(f"Detected context:\n{context_summary}\n")
    result.append(f"\n📋 Top matching SOPs (showing top {min(5, len(all_matches))}):\n")
    
    for i, (sop, score) in enumerate(all_matches[:5], 1):
        result.append(f"\n{i}. {sop.id}: {sop.title} (relevance: {score:.1f})")
        result.append(f"   Category: {sop.category} | Priority: {sop.priority}")
        result.append(f"   {sop.description}")
        if sop.applicable_departments:
            result.append(f"   Departments: {', '.join(sop.applicable_departments)}")
    
    return "\n".join(result)


def get_sop_by_id(sop_id: str) -> str:
    """
    Retrieve detailed information about a specific SOP by its ID.
    
    Args:
        sop_id: The unique identifier of the SOP (e.g., 'SOP-CARD-001')
        
    Returns:
        Detailed SOP information including all steps
    """
    if not sop_loader:
        return "Error: SOP tools not initialized"
    
    sop = sop_loader.get_sop_by_id(sop_id)
    
    if not sop:
        return f"❌ SOP '{sop_id}' not found. Use search_sops_by_context to find available SOPs."
    
    result = [f"📄 SOP Details: {sop.id}\n"]
    result.append(f"Title: {sop.title}")
    result.append(f"Category: {sop.category}")
    result.append(f"Priority: {sop.priority}")
    result.append(f"Description: {sop.description}\n")
    
    if sop.prerequisites:
        result.append(f"Prerequisites:")
        for prereq in sop.prerequisites:
            result.append(f"  • {prereq}")
        result.append("")
    
    result.append(f"Steps ({len(sop.steps)} total):\n")
    for step in sop.steps:
        result.append(f"Step {step.step_number}: {step.description}")
        if step.details:
            result.append(f"  Details: {step.details}")
        if step.estimated_time:
            result.append(f"  Time: {step.estimated_time}")
        if step.warnings:
            result.append(f"  ⚠️ Warnings: {', '.join(step.warnings)}")
        result.append("")
    
    result.append(f"\nMetadata:")
    result.append(f"  Version: {sop.metadata.version}")
    result.append(f"  Author: {sop.metadata.author}")
    result.append(f"  Status: {sop.metadata.approval_status}")
    result.append(f"  Last Updated: {sop.metadata.last_updated}")
    
    return "\n".join(result)


def start_sop_execution(sop_id: str) -> str:
    """
    Start executing a specific SOP. This begins tracking progress through the SOP steps.
    
    Args:
        sop_id: The unique identifier of the SOP to start
        
    Returns:
        Confirmation and first step details
    """
    global active_execution
    
    if not sop_loader:
        return "Error: SOP tools not initialized"
    
    sop = sop_loader.get_sop_by_id(sop_id)
    
    if not sop:
        return f"❌ SOP '{sop_id}' not found."
    
    # Create new execution
    active_execution = SOPExecution(
        sop_id=sop_id,
        started_at=datetime.now().isoformat(),
        current_step=1
    )
    
    first_step = sop.get_step(1)
    
    result = [f"✅ Started SOP: {sop.id} - {sop.title}\n"]
    result.append(f"Total Steps: {len(sop.steps)}")
    result.append(f"Priority: {sop.priority}\n")
    
    if sop.prerequisites:
        result.append("📋 Prerequisites:")
        for prereq in sop.prerequisites:
            result.append(f"  • {prereq}")
        result.append("")
    
    result.append(f"📍 Current Step: 1/{len(sop.steps)}\n")
    result.append(f"Step 1: {first_step.description}")
    if first_step.details:
        result.append(f"\nDetails: {first_step.details}")
    if first_step.estimated_time:
        result.append(f"Estimated Time: {first_step.estimated_time}")
    if first_step.validation_criteria:
        result.append(f"\nValidation Criteria:")
        for criterion in first_step.validation_criteria:
            result.append(f"  ✓ {criterion}")
    if first_step.warnings:
        result.append(f"\n⚠️ Warnings:")
        for warning in first_step.warnings:
            result.append(f"  • {warning}")
    
    return "\n".join(result)


def complete_current_step(notes: str = "") -> str:
    """
    Mark the current step as complete and move to the next step.
    
    Args:
        notes: Optional notes about the completed step
        
    Returns:
        Next step details or completion message
    """
    global active_execution
    
    if not active_execution:
        return "❌ No active SOP execution. Use start_sop_execution first."
    
    if not sop_loader:
        return "Error: SOP tools not initialized"
    
    sop = sop_loader.get_sop_by_id(active_execution.sop_id)
    if not sop:
        return f"❌ SOP '{active_execution.sop_id}' not found."
    
    # Mark current step as complete
    current_step_num = active_execution.current_step
    active_execution.completed_steps.append(current_step_num)
    
    if notes:
        active_execution.step_notes[current_step_num] = notes
    
    # Check if this was the last step
    if current_step_num >= len(sop.steps):
        active_execution.completed = True
        active_execution.completed_at = datetime.now().isoformat()
        
        result = [f"🎉 SOP Completed: {sop.id} - {sop.title}\n"]
        result.append(f"Total Steps Completed: {len(active_execution.completed_steps)}")
        result.append(f"Steps Skipped: {len(active_execution.skipped_steps)}")
        result.append(f"Completion Time: {active_execution.completed_at}")
        
        return "\n".join(result)
    
    # Move to next step
    active_execution.current_step += 1
    next_step = sop.get_step(active_execution.current_step)
    
    result = [f"✅ Step {current_step_num} completed!\n"]
    result.append(f"📍 Next Step: {active_execution.current_step}/{len(sop.steps)}\n")
    result.append(f"Step {active_execution.current_step}: {next_step.description}")
    
    if next_step.details:
        result.append(f"\nDetails: {next_step.details}")
    if next_step.estimated_time:
        result.append(f"Estimated Time: {next_step.estimated_time}")
    if next_step.validation_criteria:
        result.append(f"\nValidation Criteria:")
        for criterion in next_step.validation_criteria:
            result.append(f"  ✓ {criterion}")
    if next_step.warnings:
        result.append(f"\n⚠️ Warnings:")
        for warning in next_step.warnings:
            result.append(f"  • {warning}")
    
    return "\n".join(result)


def get_sop_progress() -> str:
    """
    Get the current progress of the active SOP execution.
    
    Returns:
        Progress summary including completed and remaining steps
    """
    if not active_execution:
        return "ℹ️ No active SOP execution. Use start_sop_execution to begin."
    
    if not sop_loader:
        return "Error: SOP tools not initialized"
    
    sop = sop_loader.get_sop_by_id(active_execution.sop_id)
    if not sop:
        return f"❌ SOP '{active_execution.sop_id}' not found."
    
    total_steps = len(sop.steps)
    completed = len(active_execution.completed_steps)
    progress_pct = (completed / total_steps) * 100
    
    result = [f"📊 SOP Progress: {sop.id} - {sop.title}\n"]
    result.append(f"Progress: {completed}/{total_steps} steps ({progress_pct:.0f}%)")
    result.append(f"Current Step: {active_execution.current_step}")
    result.append(f"Started: {active_execution.started_at}")
    
    if active_execution.skipped_steps:
        result.append(f"\nSkipped Steps: {len(active_execution.skipped_steps)}")
        for step_num, reason in active_execution.skipped_steps:
            result.append(f"  • Step {step_num}: {reason}")
    
    if not active_execution.completed:
        current_step = sop.get_step(active_execution.current_step)
        result.append(f"\n📍 Current Step {active_execution.current_step}:")
        result.append(f"{current_step.description}")
    
    return "\n".join(result)


def list_available_sops(category: Optional[str] = None) -> str:
    """
    List all available SOPs, optionally filtered by category.
    
    Args:
        category: Optional category filter (clinical, administrative, safety, etc.)
        
    Returns:
        List of available SOPs
    """
    if not sop_loader:
        return "Error: SOP tools not initialized"
    
    all_sops = sop_loader.get_all_sops()
    
    if not all_sops:
        return "📚 No SOPs currently loaded. SOPs are loaded from configured repositories."
    
    # Filter by category if specified
    if category:
        all_sops = [sop for sop in all_sops if sop.category.lower() == category.lower()]
        if not all_sops:
            return f"No SOPs found in category '{category}'"
    
    # Group by category
    by_category = {}
    for sop in all_sops:
        if sop.category not in by_category:
            by_category[sop.category] = []
        by_category[sop.category].append(sop)
    
    result = [f"📚 Available SOPs ({len(all_sops)} total):\n"]
    
    for cat, sops in sorted(by_category.items()):
        result.append(f"\n{cat.upper()} ({len(sops)} SOPs):")
        for sop in sorted(sops, key=lambda x: x.id):
            result.append(f"  • {sop.id}: {sop.title} ({sop.priority} priority)")
    
    return "\n".join(result)


def get_repository_info() -> str:
    """
    Get information about loaded SOP repositories.
    
    Returns:
        Summary of all loaded repositories
    """
    if not sop_loader:
        return "Error: SOP tools not initialized"
    
    return sop_loader.get_repository_summary()
