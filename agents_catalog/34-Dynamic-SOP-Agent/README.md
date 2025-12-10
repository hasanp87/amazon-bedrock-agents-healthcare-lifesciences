# Dynamic SOP Agent

A context-aware Standard Operating Procedure (SOP) assistant built with Strands Agents framework that dynamically loads and applies SOPs based on user context and queries.

## Overview

The Dynamic SOP Agent intelligently analyzes user queries to understand their context (department, role, task type, etc.) and dynamically loads relevant SOPs from multiple sources including local files, git repositories, and external systems via Model Context Protocol (MCP) servers.

### Key Features

🎯 **Context-Aware SOP Discovery**
- Automatically analyzes user queries to extract context (department, role, task, priority)
- Intelligently ranks and recommends relevant SOPs based on extracted context
- Learns from conversation history to improve context detection

📚 **Multi-Source SOP Integration**
- Load SOPs from local JSON/YAML files
- Integrate with git repositories via Git Repo Research MCP Server
- Connect to AWS Documentation MCP Server for service-related SOPs
- Support for custom MCP servers for organization-specific repositories

🔄 **Step-by-Step SOP Execution**
- Guides users through SOP steps with detailed instructions
- Tracks progress and completion status
- Provides warnings, validation criteria, and time estimates
- Supports step completion, skipping, and annotations

🏥 **Healthcare-Focused Design**
- Built-in support for clinical, safety, quality, and compliance SOPs
- Pre-configured categories for common healthcare departments
- Role-based SOP filtering (physician, nurse, technician, etc.)
- Priority-based SOP ranking (critical, high, medium, low)

## Project Structure

```
34-Dynamic-SOP-Agent/
├── src/                              # Source code
│   ├── agents/                       # Strands agents
│   │   ├── tools/                    # Agent tools
│   │   │   ├── sop_retrieval.py      # SOP search and retrieval
│   │   │   ├── sop_application.py    # SOP execution and tracking
│   │   │   └── context_tools.py      # Context analysis tools
│   │   └── dynamic_sop_agent.py      # Main agent class
│   ├── models/                       # Data models
│   │   └── sop_models.py             # SOP, context, and repository models
│   ├── utils/                        # Utilities
│   │   ├── sop_loader.py             # Load SOPs from files
│   │   ├── context_analyzer.py       # Context extraction and analysis
│   │   └── mcp_connector.py          # MCP server integration
│   └── __init__.py
├── tests/                            # Test suite
│   ├── test_context_analyzer.py      # Context analysis tests
│   └── test_sop_loader.py            # SOP loading tests
├── examples/                         # Example SOPs
│   └── sops/                         # Sample SOP files
│       ├── patient_admission.json    # Cardiac ICU admission
│       ├── emergency_response.yaml   # Code blue response
│       └── medication_administration.json # Safe medication admin
├── config/                           # Configuration files
├── requirements.txt                  # Python dependencies
├── main.py                           # Main application entry point
└── README.md                         # This file
```

## Setup

### Prerequisites

- Python 3.8 or higher
- Conda environment (recommended)
- Access to Amazon Bedrock (for Strands agents)

### Installation

1. **Create and activate Conda environment**:
```bash
conda create -n dynamic-sop python=3.11 -y
conda activate dynamic-sop
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

**Core Dependencies:**
- `strands-agents` - Amazon Strands framework for agent creation
- `pydantic>=2.0.0` - Data validation and models
- `pyyaml>=6.0` - YAML file parsing
- `jsonschema>=4.0.0` - JSON schema validation
- `typing-extensions>=4.0.0` - Extended type hints
- `python-dateutil>=2.8.2` - Date/time utilities

3. **Configure AWS credentials** (if using Bedrock):
```bash
aws configure
# Enter your AWS credentials when prompted
```

4. **Verify installation**:
```bash
python tests/test_sop_loader.py
python tests/test_context_analyzer.py
```

## Usage

### Quick Start

Run the interactive agent:
```bash
python main.py
```

### Basic Commands

```
💬 You: help
🤖 Assistant: [Shows available commands]

💬 You: I need to admit a cardiac patient to ICU
🤖 Assistant: [Analyzes context and suggests relevant SOPs]

💬 You: start SOP-CARD-001
🤖 Assistant: [Begins SOP execution with first step]

💬 You: complete step 1
🤖 Assistant: [Marks step complete and shows next step]

💬 You: status
🤖 Assistant: [Shows current progress]
```

## How SOPs are Discovered and Loaded Dynamically

### 1. Context Analysis

The agent analyzes user queries using the `ContextAnalyzer` to extract:

- **Category**: clinical, administrative, safety, quality, compliance, technical, operational
- **Department**: cardiology, oncology, emergency, pediatrics, radiology, pharmacy, etc.
- **Role**: physician, nurse, technician, pharmacist, administrator
- **Task Type**: admission, discharge, consultation, procedure, documentation, etc.
- **Priority**: critical, high, medium, low
- **Keywords**: Extracted from query text

**Example:**
```python
Query: "I need to admit a cardiac patient to the ICU"

Extracted Context:
  Category: clinical
  Department: cardiology
  Role: [inferred from conversation]
  Keywords: ["admit", "cardiac", "patient"]
  Priority: high
```

### 2. SOP Matching and Ranking

Once context is extracted, the agent:

1. Searches all loaded SOP repositories
2. Scores each SOP based on context match:
   - Category match: +10 points
   - Department match: +8 points
   - Role match: +5 points
   - Keyword match: +2 points per keyword
   - Priority match: +2 points
3. Ranks SOPs by relevance score
4. Presents top matches to the user

### 3. Dynamic Loading from Multiple Sources

#### Local File System
```python
agent = DynamicSOPAgent(sop_directories=["examples/sops"])
# Automatically loads all JSON and YAML files from directory
```

#### MCP Server Integration

**Git Repository SOPs:**
```python
agent.mcp_connector.connect_git_repo_mcp(
    repo_name="hospital_sops",
    repo_url="https://github.com/hospital/sop-repository",
    sop_path="procedures"
)
```

**AWS Documentation SOPs:**
```python
agent.mcp_connector.connect_aws_docs_mcp(
    service_names=["bedrock", "healthlake", "comprehendmedical"]
)
```

**Custom MCP Server:**
```python
agent.mcp_connector.connect_custom_mcp(
    name="internal_sops",
    mcp_config={
        "source_url": "https://internal.hospital.com/sops",
        "api_key": "your-api-key",
        "description": "Internal hospital SOPs"
    }
)
```

## Example Scenarios

### Scenario 1: Emergency Response

**User Query:** "Emergency code blue in room 301"

**Context Detection:**
- Category: safety
- Department: emergency
- Priority: critical
- Keywords: ["emergency", "code", "blue"]

**SOPs Loaded:**
- SOP-EMRG-001: Emergency Code Blue Response (relevance: 25.0)
- SOP-CARD-003: Post-Resuscitation Care (relevance: 12.0)

**Agent Response:**
```
🎯 Relevant SOPs for: 'Emergency code blue in room 301'

Detected context:
  • Category: safety
  • Department: emergency
  • Priority: critical

📋 Top matching SOPs:

• SOP-EMRG-001: Emergency Code Blue Response (relevance: 25.0)
  Category: safety | Priority: critical
  Rapid response protocol for cardiac arrest situations...
```

### Scenario 2: Clinical Procedure

**User Query:** "How do I safely administer IV medications"

**Context Detection:**
- Category: clinical
- Department: pharmacy
- Keywords: ["safely", "administer", "medications"]
- Priority: high

**SOPs Loaded:**
- SOP-PHARM-001: Safe Medication Administration Protocol
- SOP-SAFETY-001: IV Safety Guidelines

**Agent executes:**
1. Presents relevant SOPs
2. User selects SOP-PHARM-001
3. Guides through 10 steps (5 Rights + administration)
4. Tracks completion and provides warnings at each step

### Scenario 3: Administrative Task

**User Query:** "I need to schedule a cardiology follow-up appointment"

**Context Detection:**
- Category: administrative
- Department: cardiology
- Keywords: ["schedule", "appointment", "follow"]

**SOPs Loaded:**
- SOP-ADMIN-005: Appointment Scheduling Procedure
- SOP-CARD-010: Cardiology Follow-up Protocol

## MCP Server Configuration

### Setting Up MCP Servers

Create or edit your MCP client configuration (e.g., `~/.amazonq/mcp.json` for Amazon Q Developer):

```json
{
  "mcpServers": {
    "awslabs.git-repo-research-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.git-repo-research-mcp-server@latest"],
      "env": {
        "GITHUB_TOKEN": "your-github-token",
        "AWS_PROFILE": "your-aws-profile",
        "AWS_REGION": "us-east-1"
      },
      "disabled": false
    },
    "awslabs.aws-documentation-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "AWS_DOCUMENTATION_PARTITION": "aws"
      },
      "disabled": false
    }
  }
}
```

### Using MCP Servers in Code

```python
from src.agents.dynamic_sop_agent import DynamicSOPAgent

agent = DynamicSOPAgent()

# Connect to Git repository with SOPs
agent.register_mcp_repository(
    name="hospital_sops",
    source_type="mcp_git",
    source_url="https://github.com/yourorg/sop-repo",
    description="Hospital SOPs from Git repository"
)

# Load SOPs from the repository (with local cache)
agent.mcp_connector.load_sops_from_repository(
    "hospital_sops",
    local_cache_path="cached_sops/hospital"
)
```

## API Reference

### DynamicSOPAgent

Main agent class for SOP management and execution.

**Initialization:**
```python
agent = DynamicSOPAgent(sop_directories=["path/to/sops"])
```

**Methods:**
- `chat(message: str) -> str` - Process user message
- `load_local_sops(directory: str) -> int` - Load SOPs from directory
- `register_mcp_repository(...)` - Register external SOP repository
- `get_active_sop_summary() -> str` - Get summary of active SOP

### SOP Data Models

**SOP**: Complete standard operating procedure
```python
SOP(
    id="SOP-001",
    title="Procedure Name",
    description="Description",
    category="clinical",
    priority="high",
    steps=[...],
    metadata=SOPMetadata(...),
    applicable_departments=["dept1", "dept2"],
    applicable_roles=["role1", "role2"],
    keywords=["keyword1", "keyword2"]
)
```

**SOPContext**: Context information for SOP matching
```python
SOPContext(
    department="cardiology",
    role="physician",
    task_type="admission",
    keywords=["patient", "cardiac"],
    priority="high",
    category="clinical"
)
```

### Agent Tools

**Context Tools:**
- `analyze_context(query)` - Analyze query to extract context
- `set_context(department, role, category)` - Manually set context
- `get_context_suggestions(partial_query)` - Get SOP suggestions
- `list_context_keywords()` - List available keywords

**SOP Retrieval Tools:**
- `search_sops_by_keyword(keyword)` - Search SOPs by keyword
- `get_sop_by_id(sop_id)` - Retrieve specific SOP
- `list_available_sops(category)` - List all SOPs (optionally filtered)
- `get_sops_for_context(query)` - Get relevant SOPs for query
- `list_sop_categories()` - List all categories

**SOP Application Tools:**
- `start_sop(sop_id)` - Start executing an SOP
- `complete_step(step_number, notes)` - Mark step as complete
- `get_current_step()` - Get current step details
- `get_sop_progress()` - Get execution progress
- `skip_step(step_number, reason)` - Skip a step
- `get_step_details(step_number)` - Get details for specific step

## Creating Custom SOPs

### JSON Format

```json
{
  "id": "SOP-XXX-001",
  "title": "SOP Title",
  "description": "Brief description",
  "category": "clinical|administrative|safety|quality|compliance|technical|operational",
  "priority": "critical|high|medium|low",
  "applicable_departments": ["dept1", "dept2"],
  "applicable_roles": ["role1", "role2"],
  "keywords": ["keyword1", "keyword2"],
  "prerequisites": ["prereq1", "prereq2"],
  "steps": [
    {
      "step_number": 1,
      "description": "Step description",
      "details": "Detailed instructions",
      "required": true,
      "validation_criteria": ["criterion1", "criterion2"],
      "estimated_time": "5 minutes",
      "warnings": ["warning1", "warning2"]
    }
  ],
  "metadata": {
    "version": "1.0",
    "created_date": "2024-01-01",
    "last_updated": "2024-01-01",
    "author": "Author Name",
    "approval_status": "approved"
  }
}
```

### YAML Format

```yaml
id: SOP-XXX-001
title: SOP Title
description: Brief description
category: clinical
priority: high
applicable_departments:
  - dept1
  - dept2
applicable_roles:
  - role1
  - role2
keywords:
  - keyword1
  - keyword2
steps:
  - step_number: 1
    description: Step description
    details: Detailed instructions
    required: true
    estimated_time: 5 minutes
metadata:
  version: "1.0"
  author: Author Name
  approval_status: approved
```

## Testing

### Run Unit Tests

```bash
# Test context analyzer
python tests/test_context_analyzer.py

# Test SOP loader
python tests/test_sop_loader.py
```

### Test Coverage

Tests cover:
- Context extraction from various query types
- Category, department, and role detection
- SOP loading from JSON and YAML files
- SOP ranking and relevance scoring
- Repository management
- Step parsing and validation

## Integration with Healthcare Systems

### EHR Integration

```python
# Example: Load SOPs when patient status changes
def on_patient_status_change(patient_id, new_status):
    agent = DynamicSOPAgent()
    
    # Determine relevant SOPs based on status
    query = f"{new_status} procedure for patient"
    response = agent.chat(query)
    
    # Present SOPs to clinician
    return response
```

### Workflow Automation

```python
# Example: Automatic SOP suggestion in clinical workflow
from src.agents.dynamic_sop_agent import DynamicSOPAgent

def suggest_sops_for_task(task_description, user_role, department):
    agent = DynamicSOPAgent(sop_directories=["hospital_sops"])
    
    # Set context
    agent.context_tools.set_context(
        department=department,
        role=user_role
    )
    
    # Get relevant SOPs
    response = agent.sop_retrieval.get_sops_for_context(task_description)
    return response
```

## Architecture

### Components

1. **Dynamic SOP Agent**: Main orchestrator using Strands framework
2. **Context Analyzer**: Extracts context from natural language queries
3. **MCP Connector**: Integrates with external SOP repositories
4. **SOP Loader**: Loads SOPs from various file formats
5. **Tool Classes**: Specialized tools for retrieval, application, and context management

### Design Principles

- **Modularity**: Clear separation between context analysis, SOP loading, and execution
- **Extensibility**: Easy to add new SOP sources, categories, and tools
- **Intelligence**: Context-aware matching using relevance scoring
- **User-Friendly**: Natural language interaction via Strands agent
- **Healthcare-Focused**: Built-in support for clinical workflows and priorities

## Troubleshooting

### Common Issues

**Issue**: No SOPs loaded
```bash
Solution: Verify SOP directory path and file formats (JSON/YAML)
Check: ls examples/sops/
```

**Issue**: Context not detected correctly
```bash
Solution: Use more specific keywords or manually set context
Example: agent.chat("set context department=cardiology role=physician")
```

**Issue**: MCP server connection fails
```bash
Solution: Verify MCP server configuration and credentials
Check: MCP client configuration file
```

## Contributing

To add new SOP categories or improve context detection:

1. Edit `src/utils/context_analyzer.py` to add new keywords
2. Add example SOPs to `examples/sops/`
3. Run tests to verify changes
4. Submit pull request with description

## License

See LICENSE file in repository root.

## Support

For issues or questions:
- Check documentation in this README
- Review example SOPs in `examples/sops/`
- Run test suite to verify installation
- Open GitHub issue with details

## Version History

- **v1.0.0** (2024-12-10): Initial release
  - Context-aware SOP discovery
  - Multi-source SOP loading
  - MCP server integration
  - Step-by-step execution tracking
  - Example SOPs for healthcare workflows
