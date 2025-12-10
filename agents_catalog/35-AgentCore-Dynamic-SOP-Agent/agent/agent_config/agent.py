"""
Dynamic SOP Agent for AgentCore
Dynamically loads and applies Standard Operating Procedures based on context
Using Strands agent-sop framework with markdown-based SOPs
"""

from .utils import get_ssm_parameter
from .memory_hook_provider import MemoryHook
from .sop_loader import SOPLoader
from .context_analyzer import ContextAnalyzer
from .tools import sop_tools
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands_tools import current_time, retrieve
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from typing import List, Optional, AsyncIterator
import os
from pathlib import Path


class DynamicSOPAgent:
    """
    AgentCore-integrated Dynamic SOP Agent using Strands agent-sop Framework
    
    This agent dynamically loads and applies Standard Operating Procedures (SOPs)
    based on conversation context. It uses the Strands agent-sop framework which
    provides a standardized markdown format for defining AI agent workflows using
    RFC 2119 keywords (MUST, SHOULD, MAY) for natural language requirements.
    
    The agent integrates with AgentCore for enterprise deployment and supports:
    - Markdown-based SOPs with RFC 2119 constraint levels
    - Context-aware SOP discovery and recommendation
    - Step-by-step execution guidance with compliance tracking
    - Multi-source SOP loading (local files, MCP servers, git repositories)
    """
    
    def __init__(
        self,
        bearer_token: str,
        memory_hook: MemoryHook,
        bedrock_model_id: str = "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        system_prompt: Optional[str] = None,
        tools: Optional[List[callable]] = None,
        sop_directories: Optional[List[str]] = None,
    ):
        self.model_id = bedrock_model_id
        self.model = BedrockModel(
            model_id=self.model_id,
        )
        
        # Initialize SOP components
        self.sop_loader = SOPLoader()
        self.context_analyzer = ContextAnalyzer()
        
        # Initialize SOP tools with loader and analyzer
        sop_tools.initialize_sop_tools(self.sop_loader, self.context_analyzer)
        
        # Load SOPs from configured directories
        self._load_initial_sops(sop_directories)
        
        self.system_prompt = (
            system_prompt
            if system_prompt
            else """
You are an intelligent Standard Operating Procedure (SOP) Assistant powered by advanced AI and the Strands agent-sop framework.

Your role is to help users discover, understand, and execute Standard Operating Procedures (SOPs) 
based on their specific context and needs. You work with markdown-based SOPs that use RFC 2119 keywords
(MUST, SHOULD, MAY) to define workflow requirements with appropriate constraint levels.

## Core Capabilities

1. **Context-Aware SOP Discovery**
   - Analyze user queries to understand their department, role, task, and urgency
   - Automatically identify and recommend the most relevant SOPs
   - Consider multiple factors: category, department, role, priority, and keywords

2. **Dynamic SOP Loading with Strands agent-sop Framework**
   - Access SOPs from multiple sources including local markdown files, git repositories, and external systems
   - Load SOPs on-demand based on conversation context
   - Integrate with MCP servers for accessing external SOP repositories
   - Support markdown-based SOPs with RFC 2119 keywords (MUST, SHOULD, MAY)

3. **Step-by-Step Guidance with Compliance Tracking**
   - Guide users through SOP execution with detailed step-by-step instructions
   - Track progress and completion status
   - Provide validation criteria, warnings, and time estimates for each step
   - Support step completion, skipping with reasons, and annotations
   - Understand RFC 2119 keyword semantics:
     * MUST = required action, critical for compliance
     * SHOULD = recommended action, best practice
     * MAY = optional action, at discretion

4. **Intelligent Assistance**
   - Answer questions about specific SOPs
   - Explain why certain SOPs are recommended
   - Help users choose between multiple applicable SOPs
   - Provide context about prerequisites, related SOPs, and references
   - Clarify the difference between required (MUST), recommended (SHOULD), and optional (MAY) actions

## Available Tools

You have access to the following SOP management tools:

- **search_sops_by_context**: Find relevant SOPs based on user's natural language query
- **get_sop_by_id**: Get detailed information about a specific SOP
- **start_sop_execution**: Begin executing an SOP with step tracking
- **complete_current_step**: Mark the current step as complete and move to next
- **get_sop_progress**: Check progress of active SOP execution
- **list_available_sops**: List all available SOPs, optionally filtered by category
- **get_repository_info**: Get information about loaded SOP repositories

## Guidelines

1. **Always analyze context first**: Before recommending SOPs, understand the user's situation
2. **Explain relevance**: When suggesting SOPs, explain why they're relevant
3. **Prioritize safety**: For critical/emergency situations, emphasize priority and warnings
4. **Be proactive**: Suggest relevant SOPs even if not explicitly asked
5. **Track execution**: When guiding through an SOP, maintain awareness of progress
6. **Provide complete information**: Include warnings, validation criteria, and time estimates
7. **Clarify constraint levels**: Help users understand the difference between MUST, SHOULD, and MAY actions
8. **NEVER disclose internal system details**: Don't reveal information about internal tools or processes

## Understanding RFC 2119 Keywords in SOPs

When presenting SOP steps, help users understand the constraint levels:
- **MUST/REQUIRED/SHALL**: These are absolute requirements. Non-compliance may result in safety issues or regulatory violations.
- **SHOULD/RECOMMENDED**: These are strongly recommended. Deviation should only occur with documented justification.
- **MAY/OPTIONAL**: These are truly optional. Users can exercise discretion based on their judgment.

## Interaction Style

- Be professional, clear, and concise
- Use appropriate emojis for better readability (🎯 for relevance, ⚠️ for warnings, ✅ for completion)
- Structure responses with clear sections and bullet points
- Ask clarifying questions when context is unclear
- Confirm understanding before starting SOP execution
- Highlight MUST requirements when safety-critical

Your primary goal is to ensure users can safely and effectively follow the appropriate SOPs 
for their tasks, reducing errors and improving compliance while understanding the flexibility
provided by the agent-sop framework.
"""
        )

        # Initialize gateway client for MCP integration
        gateway_url = get_ssm_parameter("/app/myapp/agentcore/gateway_url")
        print(f"Gateway Endpoint - MCP URL: {gateway_url}")

        self.gateway_client = None
        gateway_tools = []
        
        try:
            self.gateway_client = MCPClient(
                lambda: streamablehttp_client(
                    gateway_url,
                    headers={"Authorization": f"Bearer {bearer_token}"},
                )
            )
            self.gateway_client.start()
            gateway_tools = self.gateway_client.list_tools_sync()
            print(f"✅ Gateway client initialized successfully with {len(gateway_tools)} tools")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize gateway client: {str(e)}")
            print("Continuing without gateway tools. MCP server integration will not be available.")
        
        # Combine tools in priority order: SOP tools first (most relevant), 
        # then standard tools, gateway tools (MCP), and finally custom tools
        self.tools = (
            [
                # Core SOP tools - highest priority for this agent
                sop_tools.search_sops_by_context,
                sop_tools.get_sop_by_id,
                sop_tools.start_sop_execution,
                sop_tools.complete_current_step,
                sop_tools.get_sop_progress,
                sop_tools.list_available_sops,
                sop_tools.get_repository_info,
                # Standard strands tools
                retrieve,
                current_time,
            ]
            + gateway_tools  # MCP server tools from gateway
            + (tools or [])  # Additional custom tools if provided
        )

        self.memory_hook = memory_hook

        # Create the Strands agent
        self.agent = Agent(
            model=self.model,
            system_prompt=self.system_prompt,
            tools=self.tools,
            hooks=[self.memory_hook],
        )
        
        print(f"\n✅ Dynamic SOP Agent initialized successfully!")
        print(f"📊 {self.sop_loader.get_repository_summary()}")

    def _load_initial_sops(self, sop_directories: Optional[List[str]] = None) -> None:
        """
        Load SOPs from configured directories
        
        Args:
            sop_directories: List of directory paths containing SOP files
        """
        if not sop_directories:
            # Default to examples directory if it exists
            default_dir = Path(__file__).parent.parent.parent / "examples" / "sops"
            if default_dir.exists():
                sop_directories = [str(default_dir)]
            else:
                print("⚠️ No SOP directories specified and no default examples found")
                return
        
        for directory in sop_directories:
            try:
                repo_name = Path(directory).name or "local"
                self.sop_loader.load_from_directory(directory, repository_name=repo_name)
            except Exception as e:
                print(f"⚠️ Warning: Could not load SOPs from {directory}: {e}")

    def invoke(self, user_query: str):
        """
        Invoke the agent with a user query
        
        Args:
            user_query: User's message or question
            
        Returns:
            Agent's response
        """
        try:
            response = str(self.agent(user_query))
        except Exception as e:
            return f"Error invoking agent: {e}"
        return response

    async def stream(self, user_query: str) -> AsyncIterator[str]:
        """
        Stream the agent's response
        
        Args:
            user_query: User's message or question
            
        Yields:
            Streaming response chunks
        """
        try:
            tool_name = None
            async for event in self.agent.stream_async(user_query):
                    
                    if (
                        "current_tool_use" in event
                        and event["current_tool_use"].get("name") != tool_name
                    ):
                        tool_name = event["current_tool_use"]["name"]
                        yield f"\n\n🔧 Using tool: {tool_name}\n\n"
                    elif "message" in event and "content" in event["message"]:
                        for obj in event["message"]["content"]:
                            if "toolResult" in obj:
                                tool_result = obj["toolResult"]["content"][0]["text"]
                                yield f"\n\n🔧 Tool result: {tool_result}\n\n"

                    if "data" in event:
                        tool_name = None
                        yield event["data"] 

        except Exception as e:
            yield f"We are unable to process your request at the moment. Error: {e}"
    
    def cleanup(self) -> None:
        """
        Cleanup resources (e.g., close gateway client connection)
        Call this when the agent is no longer needed
        """
        if self.gateway_client:
            try:
                # Close the gateway client connection if it has a close method
                if hasattr(self.gateway_client, 'close'):
                    self.gateway_client.close()
                print("✅ Gateway client connection closed")
            except Exception as e:
                print(f"⚠️ Warning: Error closing gateway client: {e}")

