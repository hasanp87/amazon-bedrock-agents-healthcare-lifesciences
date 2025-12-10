"""
Tools for context management and analysis
"""

from strands import tool
from typing import Optional
from ...utils.context_analyzer import ContextAnalyzer
from ...utils.mcp_connector import MCPConnector


class ContextTools:
    """Tools for managing and analyzing context"""
    
    def __init__(self, context_analyzer: ContextAnalyzer, mcp_connector: MCPConnector):
        """
        Initialize context tools
        
        Args:
            context_analyzer: ContextAnalyzer instance
            mcp_connector: MCPConnector instance
        """
        self.context_analyzer = context_analyzer
        self.mcp_connector = mcp_connector
        self.conversation_history = []
    
    @tool
    def analyze_context(self, query: str) -> str:
        """
        Analyze a query to extract context information
        
        Args:
            query: User's query or description of their task
            
        Returns:
            Formatted string with extracted context
        """
        context = self.context_analyzer.analyze_query(query, self.conversation_history)
        
        result = f"🔍 Context Analysis for: '{query}'\n\n"
        
        if context.category:
            result += f"📂 Category: {context.category}\n"
        
        if context.department:
            result += f"🏥 Department: {context.department}\n"
        
        if context.role:
            result += f"👤 Role: {context.role}\n"
        
        if context.task_type:
            result += f"📋 Task Type: {context.task_type}\n"
        
        if context.priority:
            result += f"⚡ Priority: {context.priority}\n"
        
        if context.keywords:
            result += f"\n🏷️  Keywords: {', '.join(context.keywords[:10])}\n"
        
        # Store this query in conversation history
        self.conversation_history.append(query)
        
        return result
    
    @tool
    def set_context(self, department: Optional[str] = None, role: Optional[str] = None, 
                   category: Optional[str] = None) -> str:
        """
        Manually set context parameters
        
        Args:
            department: Department name
            role: User role
            category: SOP category
            
        Returns:
            Confirmation message
        """
        result = "✅ Context updated:\n\n"
        
        if department:
            result += f"🏥 Department: {department}\n"
        
        if role:
            result += f"👤 Role: {role}\n"
        
        if category:
            result += f"📂 Category: {category}\n"
        
        # Add to conversation history to influence future context analysis
        context_msg = f"Setting context: department={department}, role={role}, category={category}"
        self.conversation_history.append(context_msg)
        
        return result
    
    @tool
    def get_context_suggestions(self, partial_query: str) -> str:
        """
        Get suggestions for relevant SOPs based on partial query
        
        Args:
            partial_query: Partial query or keywords
            
        Returns:
            Suggested SOPs and context
        """
        context = self.context_analyzer.analyze_query(partial_query)
        all_sops = self.mcp_connector.get_all_sops()
        
        if not all_sops:
            return "❌ No SOPs loaded"
        
        ranked_sops = self.context_analyzer.rank_sops_by_relevance(context, all_sops)
        relevant_sops = [(sop, score) for sop, score in ranked_sops if score > 0]
        
        result = f"💡 Suggestions based on: '{partial_query}'\n\n"
        
        if not relevant_sops:
            result += "No specific SOPs found. Try:\n"
            result += "• Being more specific about the task\n"
            result += "• Mentioning department or role\n"
            result += "• Using keywords from SOP categories\n"
            return result
        
        result += "Relevant SOPs:\n"
        for sop, score in relevant_sops[:3]:
            result += f"• {sop.id}: {sop.title} (score: {score:.1f})\n"
        
        return result
    
    @tool
    def list_context_keywords(self) -> str:
        """
        List available context keywords and categories
        
        Returns:
            Formatted list of keywords by category
        """
        result = "🏷️  Available Context Keywords:\n\n"
        
        result += "📂 CATEGORIES:\n"
        for category in ['clinical', 'administrative', 'safety', 'quality', 
                        'compliance', 'technical', 'operational']:
            result += f"  • {category}\n"
        
        result += "\n🏥 DEPARTMENTS:\n"
        result += "  • cardiology, oncology, emergency, pediatrics\n"
        result += "  • radiology, pharmacy, laboratory, surgery\n"
        
        result += "\n👤 ROLES:\n"
        result += "  • physician, nurse, technician, pharmacist\n"
        result += "  • administrator, receptionist\n"
        
        result += "\n⚡ PRIORITIES:\n"
        result += "  • critical, high, medium, low\n"
        
        return result
    
    @tool
    def clear_conversation_history(self) -> str:
        """
        Clear the conversation history
        
        Returns:
            Confirmation message
        """
        self.conversation_history = []
        return "✅ Conversation history cleared"
    
    @tool
    def get_repositories_info(self) -> str:
        """
        Get information about loaded SOP repositories
        
        Returns:
            Information about available repositories
        """
        repo_names = self.mcp_connector.list_repositories()
        
        if not repo_names:
            return "❌ No repositories loaded"
        
        result = f"📚 Loaded Repositories ({len(repo_names)}):\n\n"
        
        for repo_name in repo_names:
            repo = self.mcp_connector.get_repository(repo_name)
            result += f"• {repo.name}\n"
            result += f"  Type: {repo.source_type}\n"
            result += f"  SOPs: {len(repo.sops)}\n"
            if repo.source_url:
                result += f"  Source: {repo.source_url}\n"
            result += "\n"
        
        return result
