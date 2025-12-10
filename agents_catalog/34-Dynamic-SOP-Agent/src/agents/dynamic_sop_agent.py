"""
Dynamic SOP Agent - Main agent class for context-aware SOP loading and application
"""

from strands import Agent
from ..utils.mcp_connector import MCPConnector
from ..utils.context_analyzer import ContextAnalyzer
from ..utils.sop_loader import SOPLoader
from .tools.sop_retrieval import SOPRetrievalTools
from .tools.sop_application import SOPApplicationTools
from .tools.context_tools import ContextTools


class DynamicSOPAgent:
    """
    Dynamic SOP Agent that intelligently loads and applies Standard Operating Procedures
    based on user context and queries.
    
    This agent:
    - Analyzes user queries to extract context (department, role, task type, etc.)
    - Dynamically loads relevant SOPs from multiple sources via MCP servers
    - Guides users through SOP execution step by step
    - Tracks progress and provides real-time assistance
    """
    
    def __init__(self, sop_directories=None):
        """
        Initialize the Dynamic SOP Agent
        
        Args:
            sop_directories: List of local directories containing SOPs (optional)
        """
        # Initialize utilities
        self.mcp_connector = MCPConnector()
        self.context_analyzer = ContextAnalyzer()
        self.sop_loader = SOPLoader()
        
        # Initialize tool classes
        self.sop_retrieval = SOPRetrievalTools(self.mcp_connector, self.context_analyzer)
        self.sop_application = SOPApplicationTools(self.mcp_connector)
        self.context_tools = ContextTools(self.context_analyzer, self.mcp_connector)
        
        # Load local SOPs if directories provided
        if sop_directories:
            for directory in sop_directories:
                self.load_local_sops(directory)
        
        # Define system prompt
        system_prompt = """You are a Dynamic SOP (Standard Operating Procedure) Assistant. Your role is to help users find, understand, and execute relevant SOPs based on their context and needs.

Key Responsibilities:
1. CONTEXT ANALYSIS: Analyze user queries to understand their department, role, task type, and requirements
2. SOP DISCOVERY: Find and recommend relevant SOPs based on the extracted context
3. SOP GUIDANCE: Guide users through SOP execution step by step
4. PROGRESS TRACKING: Track progress and ensure all steps are completed properly

Available Tools:
- Context Analysis: analyze_context, set_context, get_context_suggestions, list_context_keywords
- SOP Retrieval: search_sops_by_keyword, get_sop_by_id, list_available_sops, get_sops_for_context, list_sop_categories
- SOP Execution: start_sop, complete_step, get_current_step, get_sop_progress, skip_step, get_step_details
- Repository Management: get_repositories_info, clear_conversation_history

Workflow:
1. When a user describes a task, first analyze the context
2. Search for relevant SOPs based on the context
3. Present the most relevant SOPs to the user
4. When the user selects an SOP, start the execution process
5. Guide them through each step, providing details and warnings
6. Track progress and provide encouragement

Best Practices:
- Always analyze context before searching for SOPs
- Provide clear, concise guidance for each step
- Highlight warnings and validation criteria
- Be proactive in suggesting relevant SOPs
- Track and display progress regularly
- Be supportive and encouraging during SOP execution

Example Interactions:
User: "I need to admit a cardiac patient to the ICU"
You: [Analyze context -> Search for cardiac admission SOPs -> Present relevant options]

User: "Start SOP-CARD-001"
You: [Start the SOP -> Present first step with details]

User: "Step complete"
You: [Mark step complete -> Present next step]"""

        # Initialize Strands agent with all tools
        self.agent = Agent(
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            system_prompt=system_prompt,
            tools=[
                # Context tools
                self.context_tools.analyze_context,
                self.context_tools.set_context,
                self.context_tools.get_context_suggestions,
                self.context_tools.list_context_keywords,
                self.context_tools.get_repositories_info,
                self.context_tools.clear_conversation_history,
                # SOP retrieval tools
                self.sop_retrieval.search_sops_by_keyword,
                self.sop_retrieval.get_sop_by_id,
                self.sop_retrieval.list_available_sops,
                self.sop_retrieval.get_sops_for_context,
                self.sop_retrieval.list_sop_categories,
                # SOP application tools
                self.sop_application.start_sop,
                self.sop_application.complete_step,
                self.sop_application.get_current_step,
                self.sop_application.get_sop_progress,
                self.sop_application.skip_step,
                self.sop_application.get_step_details,
            ]
        )
    
    def load_local_sops(self, directory: str) -> int:
        """
        Load SOPs from a local directory
        
        Args:
            directory: Path to directory containing SOP files
            
        Returns:
            Number of SOPs loaded
        """
        repository = self.sop_loader.load_directory(directory)
        self.mcp_connector.repositories[repository.name] = repository
        return len(repository.sops)
    
    def register_mcp_repository(self, name: str, source_type: str, source_url: str, 
                               description: str = "") -> None:
        """
        Register an MCP-based SOP repository
        
        Args:
            name: Repository name
            source_type: Type of MCP source (mcp_git, mcp_aws_docs, etc.)
            source_url: URL or path to the source
            description: Description of the repository
        """
        config = {
            'source_type': source_type,
            'source_url': source_url,
            'description': description or f'{name} repository'
        }
        self.mcp_connector.register_repository(name, config)
    
    def chat(self, message: str) -> str:
        """
        Process a user message through the agent
        
        Args:
            message: User's message
            
        Returns:
            Agent's response
        """
        try:
            # Handle special commands
            msg = message.lower().strip()
            
            if msg in ['quit', 'exit', 'bye']:
                return "👋 Goodbye! Thank you for using the Dynamic SOP Assistant."
            
            if msg in ['help', '?']:
                return self._get_help_message()
            
            if msg == 'status':
                return self.sop_application.get_sop_progress()
            
            if msg == 'repos':
                return self.context_tools.get_repositories_info()
            
            if msg == 'categories':
                return self.sop_retrieval.list_sop_categories()
            
            # Process through Strands agent
            result = self.agent(message)
            return result.content if hasattr(result, 'content') else str(result)
            
        except Exception as e:
            return f"❌ Error: {str(e)}\n\nTry 'help' for available commands."
    
    def _get_help_message(self) -> str:
        """Get help message with available commands"""
        return """🤖 Dynamic SOP Assistant - Help

BASIC COMMANDS:
• help - Show this help message
• status - Show progress on active SOP
• repos - Show loaded repositories
• categories - List SOP categories
• quit - Exit the assistant

FINDING SOPs:
• "I need to [task description]" - Analyzes context and suggests relevant SOPs
• "Search for [keyword]" - Search SOPs by keyword
• "List all SOPs" - Show all available SOPs
• "Show [category] SOPs" - List SOPs in a specific category

USING SOPs:
• "Start SOP [ID]" - Begin executing an SOP
• "Complete step [N]" - Mark step N as complete
• "Skip step [N]" - Skip a step with reason
• "Current step" - Show current step details
• "Step [N] details" - Get details for specific step

CONTEXT MANAGEMENT:
• "Analyze [query]" - Analyze context from a query
• "Set context [department/role]" - Manually set context
• "Context keywords" - List available keywords

EXAMPLES:
• "I need to admit a patient to the cardiac ICU"
• "Search for safety procedures"
• "Start SOP-CARD-001"
• "Complete step 1 - Patient vitals recorded"

For more information, just ask naturally!"""
    
    def get_active_sop_summary(self) -> str:
        """
        Get summary of the currently active SOP
        
        Returns:
            Summary of active SOP or message if none active
        """
        if self.sop_application.active_sop:
            sop = self.sop_application.active_sop
            return f"Active SOP: {sop.id} - {sop.title}\nProgress: {len(self.sop_application.completed_steps)}/{len(sop.steps)} steps"
        return "No active SOP"
