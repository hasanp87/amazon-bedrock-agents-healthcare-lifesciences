"""
Tools for SOP retrieval and search
"""

from strands import tool
from typing import List, Optional
from ...utils.mcp_connector import MCPConnector
from ...utils.context_analyzer import ContextAnalyzer
from ...models.sop_models import SOPRepository


class SOPRetrievalTools:
    """Tools for retrieving and searching SOPs"""
    
    def __init__(self, mcp_connector: MCPConnector, context_analyzer: ContextAnalyzer):
        """
        Initialize SOP retrieval tools
        
        Args:
            mcp_connector: MCPConnector instance
            context_analyzer: ContextAnalyzer instance
        """
        self.mcp_connector = mcp_connector
        self.context_analyzer = context_analyzer
    
    @tool
    def search_sops_by_keyword(self, keyword: str) -> str:
        """
        Search for SOPs by keyword
        
        Args:
            keyword: Keyword to search for in SOP titles, descriptions, and tags
            
        Returns:
            Formatted string with matching SOPs
        """
        matching_sops = self.mcp_connector.search_sops(keyword)
        
        if not matching_sops:
            return f"❌ No SOPs found matching keyword: '{keyword}'"
        
        result = f"📋 Found {len(matching_sops)} SOP(s) matching '{keyword}':\n\n"
        
        for sop in matching_sops[:5]:  # Limit to top 5
            result += f"• {sop.id}: {sop.title}\n"
            result += f"  Category: {sop.category} | Priority: {sop.priority}\n"
            result += f"  {sop.description[:100]}...\n\n"
        
        if len(matching_sops) > 5:
            result += f"... and {len(matching_sops) - 5} more\n"
        
        return result
    
    @tool
    def get_sop_by_id(self, sop_id: str) -> str:
        """
        Retrieve a specific SOP by its ID
        
        Args:
            sop_id: Unique identifier of the SOP
            
        Returns:
            Formatted string with SOP details
        """
        # Search across all repositories
        for repo_name in self.mcp_connector.list_repositories():
            repository = self.mcp_connector.get_repository(repo_name)
            sop = repository.get_sop_by_id(sop_id)
            
            if sop:
                result = f"📄 SOP {sop.id}: {sop.title}\n\n"
                result += f"Category: {sop.category}\n"
                result += f"Priority: {sop.priority}\n"
                result += f"Description: {sop.description}\n\n"
                result += f"Steps ({len(sop.steps)}):\n"
                
                for step in sop.steps:
                    result += f"  {step.step_number}. {step.description}\n"
                    if step.details:
                        result += f"     Details: {step.details}\n"
                    if step.warnings:
                        result += f"     ⚠️  Warnings: {', '.join(step.warnings)}\n"
                
                if sop.prerequisites:
                    result += f"\nPrerequisites: {', '.join(sop.prerequisites)}\n"
                
                return result
        
        return f"❌ SOP with ID '{sop_id}' not found"
    
    @tool
    def list_available_sops(self, category: Optional[str] = None) -> str:
        """
        List all available SOPs, optionally filtered by category
        
        Args:
            category: Optional category to filter by (clinical, administrative, safety, etc.)
            
        Returns:
            Formatted string with list of SOPs
        """
        all_sops = self.mcp_connector.get_all_sops()
        
        if not all_sops:
            return "❌ No SOPs currently loaded. Please load SOPs from a repository first."
        
        # Filter by category if provided
        if category:
            all_sops = [sop for sop in all_sops if sop.category.lower() == category.lower()]
            if not all_sops:
                return f"❌ No SOPs found in category: '{category}'"
        
        result = f"📚 Available SOPs ({len(all_sops)}):\n\n"
        
        # Group by category
        by_category = {}
        for sop in all_sops:
            if sop.category not in by_category:
                by_category[sop.category] = []
            by_category[sop.category].append(sop)
        
        for cat, sops in sorted(by_category.items()):
            result += f"▶ {cat.upper()}\n"
            for sop in sops:
                result += f"  • {sop.id}: {sop.title} ({sop.priority})\n"
            result += "\n"
        
        return result
    
    @tool
    def get_sops_for_context(self, query: str) -> str:
        """
        Get relevant SOPs based on a query or context
        
        Args:
            query: User's query describing their task or situation
            
        Returns:
            Formatted string with relevant SOPs
        """
        # Analyze the query to extract context
        context = self.context_analyzer.analyze_query(query)
        
        # Get all SOPs
        all_sops = self.mcp_connector.get_all_sops()
        
        if not all_sops:
            return "❌ No SOPs currently loaded. Please load SOPs from a repository first."
        
        # Rank SOPs by relevance
        ranked_sops = self.context_analyzer.rank_sops_by_relevance(context, all_sops)
        
        # Filter to only include SOPs with some relevance
        relevant_sops = [(sop, score) for sop, score in ranked_sops if score > 0]
        
        if not relevant_sops:
            return f"❌ No relevant SOPs found for: '{query}'"
        
        result = f"🎯 Relevant SOPs for: '{query}'\n\n"
        result += f"Detected context:\n"
        if context.category:
            result += f"  • Category: {context.category}\n"
        if context.department:
            result += f"  • Department: {context.department}\n"
        if context.role:
            result += f"  • Role: {context.role}\n"
        if context.priority:
            result += f"  • Priority: {context.priority}\n"
        result += "\n"
        
        result += f"📋 Top matching SOPs:\n\n"
        
        for sop, score in relevant_sops[:5]:  # Top 5
            result += f"• {sop.id}: {sop.title} (relevance: {score:.1f})\n"
            result += f"  Category: {sop.category} | Priority: {sop.priority}\n"
            result += f"  {sop.description[:80]}...\n\n"
        
        return result
    
    @tool
    def list_sop_categories(self) -> str:
        """
        List all available SOP categories
        
        Returns:
            Formatted string with available categories
        """
        all_sops = self.mcp_connector.get_all_sops()
        
        if not all_sops:
            return "❌ No SOPs currently loaded"
        
        categories = {}
        for sop in all_sops:
            if sop.category not in categories:
                categories[sop.category] = 0
            categories[sop.category] += 1
        
        result = "📂 Available SOP Categories:\n\n"
        for category, count in sorted(categories.items()):
            result += f"• {category}: {count} SOP(s)\n"
        
        return result
