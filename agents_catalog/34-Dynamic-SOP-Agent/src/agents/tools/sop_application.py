"""
Tools for applying and executing SOPs
"""

from strands import tool
from typing import Dict, Optional
from ...utils.mcp_connector import MCPConnector


class SOPApplicationTools:
    """Tools for applying and executing SOPs step by step"""
    
    def __init__(self, mcp_connector: MCPConnector):
        """
        Initialize SOP application tools
        
        Args:
            mcp_connector: MCPConnector instance
        """
        self.mcp_connector = mcp_connector
        self.active_sop = None
        self.current_step = 0
        self.completed_steps = []
        self.step_notes = {}
    
    @tool
    def start_sop(self, sop_id: str) -> str:
        """
        Start executing an SOP
        
        Args:
            sop_id: ID of the SOP to start
            
        Returns:
            Confirmation message and first step
        """
        # Find the SOP
        for repo_name in self.mcp_connector.list_repositories():
            repository = self.mcp_connector.get_repository(repo_name)
            sop = repository.get_sop_by_id(sop_id)
            
            if sop:
                self.active_sop = sop
                self.current_step = 0
                self.completed_steps = []
                self.step_notes = {}
                
                result = f"✅ Started SOP: {sop.title}\n\n"
                result += f"Total steps: {len(sop.steps)}\n"
                result += f"Priority: {sop.priority}\n"
                
                if sop.prerequisites:
                    result += f"\n⚠️  Prerequisites:\n"
                    for prereq in sop.prerequisites:
                        result += f"  • {prereq}\n"
                
                result += f"\n📍 Step 1/{len(sop.steps)}:\n"
                first_step = sop.steps[0]
                result += f"{first_step.description}\n"
                
                if first_step.details:
                    result += f"\nDetails: {first_step.details}\n"
                
                if first_step.warnings:
                    result += f"\n⚠️  Warnings:\n"
                    for warning in first_step.warnings:
                        result += f"  • {warning}\n"
                
                if first_step.estimated_time:
                    result += f"\nEstimated time: {first_step.estimated_time}\n"
                
                return result
        
        return f"❌ SOP with ID '{sop_id}' not found"
    
    @tool
    def complete_step(self, step_number: int, notes: Optional[str] = None) -> str:
        """
        Mark a step as complete and move to next step
        
        Args:
            step_number: Number of the step to mark complete
            notes: Optional notes about the step completion
            
        Returns:
            Confirmation and next step information
        """
        if not self.active_sop:
            return "❌ No active SOP. Use start_sop() first."
        
        if step_number not in range(1, len(self.active_sop.steps) + 1):
            return f"❌ Invalid step number. SOP has {len(self.active_sop.steps)} steps."
        
        # Mark step as completed
        if step_number not in self.completed_steps:
            self.completed_steps.append(step_number)
        
        if notes:
            self.step_notes[step_number] = notes
        
        result = f"✅ Completed step {step_number}/{len(self.active_sop.steps)}\n"
        
        if notes:
            result += f"Notes: {notes}\n"
        
        # Check if there are more steps
        if step_number < len(self.active_sop.steps):
            next_step = self.active_sop.steps[step_number]  # 0-indexed
            self.current_step = step_number
            
            result += f"\n📍 Next Step {step_number + 1}/{len(self.active_sop.steps)}:\n"
            result += f"{next_step.description}\n"
            
            if next_step.details:
                result += f"\nDetails: {next_step.details}\n"
            
            if next_step.warnings:
                result += f"\n⚠️  Warnings:\n"
                for warning in next_step.warnings:
                    result += f"  • {warning}\n"
            
            if next_step.estimated_time:
                result += f"\nEstimated time: {next_step.estimated_time}\n"
        else:
            result += f"\n🎉 SOP '{self.active_sop.title}' completed!\n"
            result += f"Total steps completed: {len(self.completed_steps)}\n"
        
        return result
    
    @tool
    def get_current_step(self) -> str:
        """
        Get information about the current step
        
        Returns:
            Current step information
        """
        if not self.active_sop:
            return "❌ No active SOP"
        
        if self.current_step >= len(self.active_sop.steps):
            return "✅ All steps completed"
        
        step = self.active_sop.steps[self.current_step]
        
        result = f"📍 Current Step {self.current_step + 1}/{len(self.active_sop.steps)}:\n"
        result += f"{step.description}\n"
        
        if step.details:
            result += f"\nDetails: {step.details}\n"
        
        if step.validation_criteria:
            result += f"\n✓ Validation Criteria:\n"
            for criterion in step.validation_criteria:
                result += f"  • {criterion}\n"
        
        if step.warnings:
            result += f"\n⚠️  Warnings:\n"
            for warning in step.warnings:
                result += f"  • {warning}\n"
        
        if step.estimated_time:
            result += f"\nEstimated time: {step.estimated_time}\n"
        
        return result
    
    @tool
    def get_sop_progress(self) -> str:
        """
        Get progress information for the active SOP
        
        Returns:
            Progress summary
        """
        if not self.active_sop:
            return "❌ No active SOP"
        
        total_steps = len(self.active_sop.steps)
        completed = len(self.completed_steps)
        progress_pct = (completed / total_steps) * 100
        
        result = f"📊 SOP Progress: {self.active_sop.title}\n\n"
        result += f"Steps completed: {completed}/{total_steps} ({progress_pct:.1f}%)\n"
        result += f"Current step: {self.current_step + 1}\n\n"
        
        result += "Steps:\n"
        for i, step in enumerate(self.active_sop.steps, 1):
            status = "✅" if i in self.completed_steps else "⏳"
            marker = "👉 " if i == self.current_step + 1 else "   "
            result += f"{marker}{status} Step {i}: {step.description[:50]}...\n"
        
        return result
    
    @tool
    def skip_step(self, step_number: int, reason: str) -> str:
        """
        Skip a step with a reason
        
        Args:
            step_number: Number of the step to skip
            reason: Reason for skipping
            
        Returns:
            Confirmation message
        """
        if not self.active_sop:
            return "❌ No active SOP"
        
        if step_number not in range(1, len(self.active_sop.steps) + 1):
            return f"❌ Invalid step number"
        
        self.step_notes[step_number] = f"SKIPPED: {reason}"
        
        result = f"⏭️  Skipped step {step_number}\n"
        result += f"Reason: {reason}\n"
        
        # Move to next step if this was the current step
        if step_number == self.current_step + 1:
            self.current_step = step_number
            if step_number < len(self.active_sop.steps):
                next_step = self.active_sop.steps[step_number]
                result += f"\n📍 Next Step {step_number + 1}/{len(self.active_sop.steps)}:\n"
                result += f"{next_step.description}\n"
        
        return result
    
    @tool
    def get_step_details(self, step_number: int) -> str:
        """
        Get detailed information about a specific step
        
        Args:
            step_number: Number of the step
            
        Returns:
            Detailed step information
        """
        if not self.active_sop:
            return "❌ No active SOP"
        
        step = self.active_sop.get_step(step_number)
        if not step:
            return f"❌ Step {step_number} not found"
        
        result = f"📋 Step {step_number} Details:\n\n"
        result += f"{step.description}\n"
        
        if step.details:
            result += f"\n📝 Details:\n{step.details}\n"
        
        if step.validation_criteria:
            result += f"\n✓ Validation Criteria:\n"
            for criterion in step.validation_criteria:
                result += f"  • {criterion}\n"
        
        if step.warnings:
            result += f"\n⚠️  Warnings:\n"
            for warning in step.warnings:
                result += f"  • {warning}\n"
        
        if step.estimated_time:
            result += f"\n⏱️  Estimated time: {step.estimated_time}\n"
        
        result += f"\nRequired: {'Yes' if step.required else 'No'}\n"
        
        if step_number in self.step_notes:
            result += f"\n📌 Notes: {self.step_notes[step_number]}\n"
        
        return result
