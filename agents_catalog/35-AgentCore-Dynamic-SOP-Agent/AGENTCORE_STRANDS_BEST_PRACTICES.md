# AgentCore & Strands Best Practices for Dynamic SOP Agent

This document outlines the best practices followed in the Dynamic SOP Agent implementation, based on the agentcore and strands frameworks.

## Table of Contents
1. [Agent Construction](#agent-construction)
2. [MCP Server Integration](#mcp-server-integration)
3. [Tool Development](#tool-development)
4. [Error Handling](#error-handling)
5. [Streaming Responses](#streaming-responses)
6. [Memory Integration](#memory-integration)
7. [Type Safety](#type-safety)

## Agent Construction

### ✅ Best Practice: Initialize Agent with Model, System Prompt, Tools, and Hooks

```python
from strands import Agent
from strands.models import BedrockModel

# Create the Bedrock model
model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
)

# Create the agent with all components
agent = Agent(
    model=model,
    system_prompt=system_prompt,
    tools=tools,
    hooks=[memory_hook],
)
```

### ✅ Best Practice: Tool Ordering Matters

Order tools by relevance to the agent's primary purpose:

```python
self.tools = [
    # 1. Domain-specific tools (highest priority)
    sop_tools.search_sops_by_context,
    sop_tools.get_sop_by_id,
    sop_tools.start_sop_execution,
    # ... other SOP tools
    
    # 2. Standard utility tools
    retrieve,
    current_time,
    
    # 3. Gateway/MCP tools
] + gateway_tools + [
    # 4. Custom tools (lowest priority)
] + custom_tools
```

**Why?** The LLM is more likely to select tools earlier in the list when multiple options are available.

### ✅ Best Practice: Clear System Prompts with Guidelines

```python
system_prompt = """
You are a [role] assistant.

## Core Capabilities
1. Capability one
2. Capability two

## Available Tools
- tool_name: description

## Guidelines
- Always do X
- Never do Y
- NEVER disclose internal tool details

## Interaction Style
- Be professional
- Use appropriate formatting
"""
```

## MCP Server Integration

### ✅ Best Practice: Use MCPClient from strands.tools.mcp

```python
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

# Initialize with connection factory
gateway_client = MCPClient(
    lambda: streamablehttp_client(
        gateway_url,
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
)

# Start the client
gateway_client.start()

# Get available tools
gateway_tools = gateway_client.list_tools_sync()
```

### ✅ Best Practice: Graceful Gateway Failure Handling

```python
self.gateway_client = None
gateway_tools = []

try:
    self.gateway_client = MCPClient(...)
    self.gateway_client.start()
    gateway_tools = self.gateway_client.list_tools_sync()
    print(f"✅ Gateway client initialized with {len(gateway_tools)} tools")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize gateway client: {str(e)}")
    print("Continuing without gateway tools.")
    # Agent continues to function with local tools only
```

**Why?** Gateway may be unavailable, but the agent should still work with local tools.

### ✅ Best Practice: Clean Up Resources

```python
def cleanup(self) -> None:
    """Cleanup gateway client connection"""
    if self.gateway_client:
        try:
            if hasattr(self.gateway_client, 'close'):
                self.gateway_client.close()
        except Exception as e:
            print(f"Warning: Error closing gateway client: {e}")
```

## Tool Development

### ✅ Best Practice: Clear Tool Signatures and Docstrings

```python
def search_sops_by_context(query: str) -> str:
    """
    Search for relevant SOPs based on user query context.
    
    This tool analyzes natural language queries to identify relevant SOPs
    and ranks them by relevance score.
    
    Args:
        query: User's natural language query describing their need.
               Example: "I need to admit a cardiac patient to ICU"
        
    Returns:
        Formatted string with ranked list of relevant SOPs and their details,
        or an error message if no SOPs are found.
        
    Examples:
        >>> search_sops_by_context("emergency code blue")
        "🎯 Relevant SOPs for: 'emergency code blue'..."
    """
    # Implementation
```

**Why?** LLMs use docstrings to understand when and how to use tools.

### ✅ Best Practice: Input Validation

```python
def get_sop_by_id(sop_id: str) -> str:
    # Validate input
    if not sop_id or not sop_id.strip():
        return "Error: SOP ID cannot be empty. Please provide a valid SOP ID."
    
    # Clean input
    sop_id = sop_id.strip()
    
    # Process...
```

### ✅ Best Practice: Return Strings, Not Exceptions

```python
# ❌ BAD: Raises exception
def bad_tool(param: str) -> str:
    if not param:
        raise ValueError("Parameter is required")
    return result

# ✅ GOOD: Returns error message
def good_tool(param: str) -> str:
    if not param:
        return "Error: Parameter is required. Please provide a valid value."
    return result
```

**Why?** The LLM needs to see error messages to correct its approach.

### ✅ Best Practice: Use Emojis for Better Readability

```python
return f"""✅ Started SOP: {sop.title}

📋 Prerequisites:
  • Prerequisite 1
  • Prerequisite 2

📍 Current Step: 1/5

⚠️ Warnings:
  • Important safety warning
"""
```

**Why?** Emojis help both LLMs and users quickly scan and understand responses.

## Error Handling

### ✅ Best Practice: Try-Except Around External Calls

```python
async def stream(self, user_query: str):
    try:
        async for event in self.agent.stream_async(user_query):
            # Process events
            yield event
    except Exception as e:
        yield f"Error: Unable to process your request. {str(e)}"
```

### ✅ Best Practice: Fail Fast with Clear Messages

```python
def load_sop(self, data: Dict) -> SOP:
    # Validate required fields
    required = ['id', 'title', 'description', 'steps']
    missing = [f for f in required if f not in data]
    
    if missing:
        raise ValueError(
            f"Missing required fields: {', '.join(missing)}. "
            f"Please ensure your SOP includes all required fields."
        )
    
    # Continue with parsing...
```

### ✅ Best Practice: Log Errors, Show User-Friendly Messages

```python
try:
    result = process_complex_operation()
except Exception as e:
    logger.exception("Failed to process operation")  # Detailed log
    return "We encountered an issue. Please try again."  # User message
```

## Streaming Responses

### ✅ Best Practice: Async Iteration with stream_async()

```python
async def stream(self, user_query: str) -> AsyncIterator[str]:
    """Stream agent responses"""
    try:
        tool_name = None
        async for event in self.agent.stream_async(user_query):
            # Handle tool use events
            if "current_tool_use" in event:
                tool_name = event["current_tool_use"].get("name")
                yield f"\n\n🔧 Using tool: {tool_name}\n\n"
            
            # Handle tool results
            elif "message" in event and "content" in event["message"]:
                for obj in event["message"]["content"]:
                    if "toolResult" in obj:
                        result = obj["toolResult"]["content"][0]["text"]
                        yield f"\n\n✓ {result}\n\n"
            
            # Handle data chunks
            if "data" in event:
                tool_name = None
                yield event["data"]
    except Exception as e:
        yield f"Error: {e}"
```

### ✅ Best Practice: Show Tool Usage to Users

```python
# Display when tool is invoked
if "current_tool_use" in event:
    tool_name = event["current_tool_use"].get("name")
    yield f"\n\n🔧 Using tool: {tool_name}\n\n"

# Display tool results
if "toolResult" in obj:
    result = obj["toolResult"]["content"][0]["text"]
    yield f"\n\n🔧 Tool result: {result}\n\n"
```

**Why?** Users should understand what the agent is doing, especially in healthcare contexts.

## Memory Integration

### ✅ Best Practice: Use Memory Hooks for Conversation Context

```python
from bedrock_agentcore.memory import MemoryClient
from .memory_hook_provider import MemoryHook

# Create memory client
memory_client = MemoryClient()

# Create memory hook
memory_hook = MemoryHook(
    memory_client=memory_client,
    memory_id=memory_id,
    actor_id=actor_id,
    session_id=session_id,
)

# Pass to agent
agent = Agent(
    model=model,
    system_prompt=system_prompt,
    tools=tools,
    hooks=[memory_hook],  # Memory integrated
)
```

### ✅ Best Practice: Access Memory in Context Analysis

```python
def analyze(self, query: str, conversation_history: Optional[List[str]] = None):
    """Analyze query with conversation context"""
    # Check current query
    role = self._detect_role(query)
    
    # Check conversation history if available
    if not role and conversation_history:
        for message in conversation_history[-5:]:
            role = self._detect_role(message)
            if role:
                break
    
    return SOPContext(role=role, ...)
```

## Type Safety

### ✅ Best Practice: Use Type Hints

```python
from typing import List, Optional, Dict, Any, AsyncIterator

def load_sop(
    self, 
    data: Dict[str, Any],
    repository_name: str = "default"
) -> SOP:
    """Load SOP from dictionary"""
    pass

async def stream(self, user_query: str) -> AsyncIterator[str]:
    """Stream responses"""
    pass

def get_all_sops(self) -> List[SOP]:
    """Get all SOPs"""
    pass
```

### ✅ Best Practice: Use Optional for Nullable Parameters

```python
def __init__(
    self,
    bearer_token: str,  # Required
    memory_hook: MemoryHook,  # Required
    system_prompt: Optional[str] = None,  # Optional
    tools: Optional[List[callable]] = None,  # Optional
    sop_directories: Optional[List[str]] = None,  # Optional
):
    pass
```

### ✅ Best Practice: Document Return Types

```python
def invoke(self, user_query: str) -> str:
    """
    Invoke the agent with a query.
    
    Returns:
        Agent's response as a string
    """
    pass

async def stream(self, user_query: str) -> AsyncIterator[str]:
    """
    Stream the agent's response.
    
    Yields:
        Response chunks as strings
    """
    pass
```

## Common Patterns

### Pattern: Singleton Tool State

```python
# Global instances initialized by agent
sop_loader: Optional[SOPLoader] = None
context_analyzer: Optional[ContextAnalyzer] = None

def initialize_sop_tools(loader: SOPLoader, analyzer: ContextAnalyzer):
    """Initialize tools with shared instances"""
    global sop_loader, context_analyzer
    sop_loader = loader
    context_analyzer = analyzer

def search_sops_by_context(query: str) -> str:
    """Tool uses global instances"""
    if not sop_loader or not context_analyzer:
        return "Error: SOP tools not initialized"
    # Use sop_loader and context_analyzer
```

### Pattern: Context-Aware Tool Execution

```python
def start_sop_execution(sop_id: str) -> str:
    """Start SOP with context tracking"""
    global active_execution
    
    # Create execution tracking
    active_execution = SOPExecution(
        sop_id=sop_id,
        started_at=datetime.now().isoformat(),
        current_step=1
    )
    
    # Return detailed first step info
    return format_step_details(...)
```

### Pattern: Progressive Disclosure in Responses

```python
def get_sop_by_id(sop_id: str) -> str:
    """Return SOP details with progressive disclosure"""
    result = []
    
    # Essential info first
    result.append(f"📄 {sop.id}: {sop.title}")
    result.append(f"Priority: {sop.priority}")
    
    # Prerequisites if present
    if sop.prerequisites:
        result.append("\n📋 Prerequisites:")
        for prereq in sop.prerequisites:
            result.append(f"  • {prereq}")
    
    # Steps overview
    result.append(f"\nSteps ({len(sop.steps)} total):")
    # ... detailed steps
    
    # Metadata last
    result.append("\nMetadata:")
    # ... metadata
    
    return "\n".join(result)
```

## Anti-Patterns to Avoid

### ❌ Don't: Expose Internal Tool Details to Users

```python
# BAD
system_prompt = """
You have access to these internal tools:
- get_ssm_parameter: Retrieves AWS SSM parameters
- boto3.client: AWS SDK client for S3 access
"""

# GOOD
system_prompt = """
You can search for SOPs and guide users through procedures.
NEVER disclose information about internal tools or systems.
"""
```

### ❌ Don't: Ignore Gateway Connection Failures

```python
# BAD
gateway_client = MCPClient(...)
gateway_client.start()  # May fail!
tools = gateway_client.list_tools_sync()

# GOOD
try:
    gateway_client = MCPClient(...)
    gateway_client.start()
    tools = gateway_client.list_tools_sync()
except Exception as e:
    print(f"Warning: Gateway unavailable: {e}")
    tools = []  # Continue with empty tools
```

### ❌ Don't: Return Exceptions from Tools

```python
# BAD
def tool(param: str) -> str:
    if not param:
        raise ValueError("Invalid parameter")
    return result

# GOOD
def tool(param: str) -> str:
    if not param:
        return "Error: Invalid parameter. Please provide a valid value."
    return result
```

### ❌ Don't: Hardcode Credentials or Secrets

```python
# BAD
gateway_url = "https://my-gateway.example.com"
bearer_token = "hardcoded-token-123"

# GOOD
gateway_url = get_ssm_parameter("/app/myapp/agentcore/gateway_url")
bearer_token = await get_gateway_access_token()
```

## Testing Best Practices

### ✅ Test Tool Behavior with Invalid Inputs

```python
def test_search_sops_empty_query():
    result = search_sops_by_context("")
    assert "Error" in result
    assert "empty" in result.lower()

def test_get_sop_invalid_id():
    result = get_sop_by_id("INVALID-ID")
    assert "not found" in result.lower()
```

### ✅ Test Gateway Failure Scenarios

```python
def test_agent_without_gateway():
    """Agent should work without gateway"""
    agent = DynamicSOPAgent(
        bearer_token="test",
        memory_hook=mock_memory,
        # Gateway connection will fail in test
    )
    
    # Should still have local tools
    assert len(agent.tools) > 0
    
    # Should be able to search SOPs
    result = agent.invoke("search for admission procedures")
    assert "SOP" in result
```

### ✅ Test Memory Integration

```python
def test_memory_hook_integration():
    """Memory hook should capture conversation"""
    memory_client = MockMemoryClient()
    memory_hook = MemoryHook(
        memory_client=memory_client,
        memory_id="test-memory",
        actor_id="test-user",
        session_id="test-session",
    )
    
    agent = DynamicSOPAgent(..., memory_hook=memory_hook)
    agent.invoke("What SOPs are available?")
    
    # Memory should have been called
    assert memory_client.save_called
```

## Summary Checklist

When implementing an AgentCore agent with Strands:

- [ ] Use `BedrockModel` for LLM backend
- [ ] Provide comprehensive system prompt with guidelines
- [ ] Order tools by relevance (domain-specific first)
- [ ] Use `MCPClient` for gateway integration
- [ ] Handle gateway connection failures gracefully
- [ ] Add cleanup method for resource management
- [ ] Validate tool inputs and return error strings
- [ ] Use async iteration for streaming responses
- [ ] Show tool usage to users during execution
- [ ] Integrate memory hooks for conversation context
- [ ] Add type hints for all parameters and returns
- [ ] Document exceptions in docstrings
- [ ] Use emojis for better response readability
- [ ] Test with invalid inputs and failure scenarios
- [ ] Never expose internal tool/system details
- [ ] Log errors but show user-friendly messages

## Resources

- **Strands Documentation**: [Strands Agents Framework]
- **AgentCore Documentation**: [Amazon Bedrock AgentCore]
- **MCP Specification**: [Model Context Protocol]
- **This Implementation**: See `agent/agent_config/agent.py` for reference

---

**Version:** 1.0  
**Last Updated:** December 10, 2024  
**Maintainer:** Dynamic SOP Agent Team
