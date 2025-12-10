# AgentCore Dynamic SOP Agent

A context-aware Standard Operating Procedure (SOP) assistant built with the Strands Agents framework and integrated with Amazon Bedrock AgentCore for enterprise deployment. This agent dynamically loads and applies SOPs based on user context and queries.

## Overview

The AgentCore Dynamic SOP Agent intelligently analyzes user queries to understand their context (department, role, task type, etc.) and dynamically loads relevant SOPs from multiple sources. It's designed for healthcare and enterprise environments requiring strict adherence to standard operating procedures.

### Key Features

🎯 **Context-Aware SOP Discovery**
- Automatically analyzes user queries to extract context (department, role, task, priority)
- Intelligently ranks and recommends relevant SOPs based on extracted context
- Learns from conversation to improve context detection

📚 **Multi-Source SOP Integration**
- Load SOPs from local JSON/YAML files
- Integrate with git repositories via MCP Server
- Connect to external systems through AgentCore Gateway
- Support for custom MCP servers for organization-specific repositories

🔄 **Step-by-Step SOP Execution**
- Guides users through SOP steps with detailed instructions
- Tracks progress and completion status
- Provides warnings, validation criteria, and time estimates
- Supports step completion, skipping, and annotations

🏢 **Enterprise-Ready with AgentCore**
- Integrated with Amazon Bedrock AgentCore for production deployment
- OAuth and IAM authentication support
- Memory integration for conversation context
- Streamlit UI for easy interaction
- CloudWatch observability and monitoring

## Architecture

This agent follows the AgentCore template structure and integrates:

1. **Strands Agents Framework**: Core AI agent capabilities
2. **Amazon Bedrock AgentCore**: Enterprise deployment infrastructure
3. **MCP Server Integration**: External SOP repository access
4. **Memory System**: Conversation and preference tracking
5. **Gateway Integration**: Access to lambda-based tools

## Project Structure

```
35-AgentCore-Dynamic-SOP-Agent/
├── agent/
│   ├── agent_config/
│   │   ├── agent.py                    # Main DynamicSOPAgent class
│   │   ├── sop_models.py               # SOP data models
│   │   ├── sop_loader.py               # Load SOPs from various sources
│   │   ├── context_analyzer.py         # Context extraction logic
│   │   ├── agent_task.py               # Agent task orchestration
│   │   ├── tools/
│   │   │   └── sop_tools.py            # SOP retrieval and execution tools
│   │   ├── memory_hook_provider.py     # Memory integration
│   │   ├── access_token.py             # OAuth token management
│   │   ├── streaming_queue.py          # Response streaming
│   │   └── utils.py                    # Utility functions
│   └── requirements.txt                # Python dependencies
├── examples/
│   └── sops/                           # Example SOP files
│       ├── patient_admission.json      # Cardiac ICU admission SOP
│       ├── emergency_response.yaml     # Code blue response SOP
│       └── medication_administration.json  # Medication safety SOP
├── tests/
│   ├── test_sop_loader.py              # SOP loader tests
│   └── test_context_analyzer.py        # Context analysis tests
├── scripts/                            # Deployment and management scripts
│   ├── agentcore_gateway.py            # Gateway management
│   ├── agentcore_memory.py             # Memory management
│   ├── agentcore_agent_runtime.py      # Runtime management
│   └── cognito_credentials_provider.py # OAuth setup
├── prerequisite/                       # Infrastructure setup
│   ├── infrastructure.yaml             # CloudFormation template
│   ├── cognito.yaml                    # Cognito setup
│   └── lambda/                         # Lambda function code
├── app_modules/                        # Streamlit UI modules
├── config/                             # Configuration files
├── main.py                             # AgentCore entry point
├── app.py                              # Streamlit app (IAM auth)
├── app_oauth.py                        # Streamlit app (OAuth)
└── README.md                           # This file
```

## Prerequisites

### AWS Account Setup

1. **AWS Account**: Active AWS account with appropriate permissions
   - [Create AWS Account](https://aws.amazon.com/account/)

2. **AWS CLI**: Install and configure AWS CLI
   ```bash
   aws configure
   ```

3. **Bedrock Model Access**: Enable access to Claude models
   - Navigate to [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
   - Request access to:
     - Anthropic Claude 3.7 Sonnet
     - Anthropic Claude 3.5 Haiku

4. **Python 3.10+**: Required for running the application

## Setup and Deployment

### 1. Create Infrastructure

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r dev-requirements.txt

chmod +x scripts/prereq.sh
./scripts/prereq.sh

chmod +x scripts/list_ssm_parameters.sh
./scripts/list_ssm_parameters.sh
```

> **Note**: Prefix all resource names with your chosen prefix (e.g., `myapp`).

### 2. Create AgentCore Gateway

The gateway provides access to Lambda-based tools and MCP servers:

```bash
python scripts/agentcore_gateway.py create --name myapp-gw
```

### 3. Setup AgentCore Identity (OAuth)

```bash
python scripts/cognito_credentials_provider.py create --name myapp-cp
```

### 4. Create Memory

```bash
python scripts/agentcore_memory.py create --name myapp

# Test memory
python tests/test_memory.py load-conversation
python tests/test_memory.py list-memory
```

### 5. Setup Agent Runtime

```bash
agentcore configure --entrypoint main.py -rf agent/requirements.txt \
  -er arn:aws:iam::<Account-Id>:role/<Role> --name myappDynamicSOPAgent
```

Use `./scripts/list_ssm_parameters.sh` to get:
- Role = `/app/myapp/agentcore/runtime_iam_role`
- OAuth Discovery URL = `/app/myapp/agentcore/cognito_discovery_url`
- OAuth client id = `/app/myapp/agentcore/web_client_id`

Deploy the agent:

```bash
rm .agentcore.yaml  # Clean up before launch
agentcore launch
```

**Test the agent:**

IAM authentication:
```bash
agentcore invoke '{"prompt": "What SOPs are available?"}'
```

OAuth authentication:
```bash
python tests/test_agent.py myappDynamicSOPAgent -p "What SOPs are available?"
```

### 6. Run Streamlit UI

**IAM Authentication:**
```bash
streamlit run app.py --server.port 8501
```

**OAuth Authentication:**
```bash
streamlit run app_oauth.py --server.port 8501 -- --agent=myappDynamicSOPAgent
```

## How SOPs are Discovered and Loaded Dynamically

### 1. Context Analysis

When a user makes a query, the agent analyzes it to extract:

- **Category**: clinical, administrative, safety, quality, compliance, technical, operational
- **Department**: cardiology, oncology, emergency, pediatrics, radiology, pharmacy, etc.
- **Role**: physician, nurse, technician, pharmacist, administrator
- **Task Type**: admission, discharge, consultation, procedure, documentation, etc.
- **Priority**: critical, high, medium, low
- **Keywords**: Extracted from query text

**Example:**
```
Query: "I need to admit a cardiac patient to the ICU"

Extracted Context:
  Category: clinical
  Department: cardiology
  Role: [inferred from conversation]
  Task: admission
  Keywords: ["admit", "cardiac", "patient", "icu"]
  Priority: high
```

### 2. SOP Matching and Ranking

The agent scores each SOP based on context match:
- Category match: +10 points
- Department match: +8 points
- Role match: +5 points
- Priority match: +2 points
- Keyword match: +2 points per keyword

SOPs are ranked by relevance score and presented to the user.

### 3. Dynamic Loading from Multiple Sources

#### Local File System
```python
# SOPs are loaded from examples/sops/ directory on startup
# Supports JSON and YAML formats
```

#### MCP Server Integration

**Configure MCP servers** for external SOP repositories:

Create `~/.amazonq/mcp.json`:
```json
{
  "mcpServers": {
    "git-repo-sops": {
      "command": "uvx",
      "args": ["awslabs.git-repo-research-mcp-server@latest"],
      "env": {
        "GITHUB_TOKEN": "your-token"
      }
    }
  }
}
```

**Access SOPs** through AgentCore Gateway:
```python
# Gateway automatically integrates MCP server tools
# Agent can search and retrieve SOPs from external repositories
```

## Example Usage Scenarios

### Scenario 1: Emergency Response

**User Query:** "Emergency code blue in room 301"

**Agent Response:**
```
🎯 Relevant SOPs for: 'Emergency code blue in room 301'

Detected context:
  • Category: safety
  • Department: emergency
  • Priority: critical

📋 Top matching SOPs:

1. SOP-EMRG-001: Emergency Code Blue Response Protocol (relevance: 25.0)
   Category: safety | Priority: critical
   Rapid response protocol for cardiac arrest situations...
```

**Starting SOP Execution:**
```
User: Start SOP-EMRG-001

Agent: ✅ Started SOP: SOP-EMRG-001 - Emergency Code Blue Response Protocol

Total Steps: 7
Priority: critical

📋 Prerequisites:
  • Code blue cart accessible and stocked
  • Defibrillator charged and ready
  • Team members trained in ACLS

📍 Current Step: 1/7

Step 1: Activate code blue and assess scene safety
Details: Call code blue overhead, announce location, ensure scene is safe...
Estimated Time: 30 seconds

⚠️ Warnings:
  • Ensure scene safety before proceeding
  • Do not delay calling for help
```

### Scenario 2: Clinical Procedure

**User Query:** "How do I safely administer IV medications"

**Context Detection:**
- Category: clinical
- Department: pharmacy
- Keywords: ["safely", "administer", "medications"]
- Priority: high

**Agent provides:** Relevant medication administration SOP with step-by-step guidance through the 5 Rights of medication administration.

### Scenario 3: Patient Admission

**User Query:** "I need to admit a cardiac patient to ICU"

**Agent Response:** Recommends SOP-CARD-001 (Cardiac ICU Patient Admission Protocol) and guides through 6 steps including verification, assessment, monitoring setup, and documentation.

## Available Agent Tools

The agent has access to the following SOP management tools:

### Context and Discovery Tools
- `search_sops_by_context(query)` - Find relevant SOPs based on natural language query
- `list_available_sops(category)` - List all SOPs, optionally filtered by category
- `get_repository_info()` - Get information about loaded SOP repositories

### SOP Retrieval Tools
- `get_sop_by_id(sop_id)` - Get detailed information about a specific SOP

### SOP Execution Tools
- `start_sop_execution(sop_id)` - Begin executing an SOP with step tracking
- `complete_current_step(notes)` - Mark current step as complete and move to next
- `get_sop_progress()` - Check progress of active SOP execution

## Creating Custom SOPs

### JSON Format

```json
{
  "id": "SOP-XXX-001",
  "title": "SOP Title",
  "description": "Brief description",
  "category": "clinical",
  "priority": "high",
  "applicable_departments": ["dept1", "dept2"],
  "applicable_roles": ["role1", "role2"],
  "keywords": ["keyword1", "keyword2"],
  "prerequisites": ["prereq1"],
  "steps": [
    {
      "step_number": 1,
      "description": "Step description",
      "details": "Detailed instructions",
      "required": true,
      "validation_criteria": ["criterion1"],
      "estimated_time": "5 minutes",
      "warnings": ["warning1"]
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
keywords:
  - keyword1
  - keyword2
steps:
  - step_number: 1
    description: Step description
    required: true
    estimated_time: 5 minutes
metadata:
  version: "1.0"
  author: Author Name
  approval_status: approved
```

Place SOP files in the `examples/sops/` directory, and they will be automatically loaded on agent startup.

## Testing

### Run Unit Tests

```bash
# Test SOP loader
python tests/test_sop_loader.py

# Test context analyzer
python tests/test_context_analyzer.py
```

**Test Coverage:**
- Context extraction from various query types
- Category, department, and role detection
- SOP loading from JSON and YAML files
- SOP ranking and relevance scoring
- Repository management

## MCP Server Configuration

### Example MCP Configuration

Create or edit `~/.amazonq/mcp.json`:

```json
{
  "mcpServers": {
    "git-repo-sops": {
      "command": "uvx",
      "args": ["awslabs.git-repo-research-mcp-server@latest"],
      "env": {
        "GITHUB_TOKEN": "your-github-token",
        "AWS_PROFILE": "your-aws-profile"
      }
    },
    "aws-docs": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "AWS_DOCUMENTATION_PARTITION": "aws"
      }
    }
  }
}
```

### Using MCP Servers

The agent automatically integrates with MCP servers configured in the AgentCore Gateway. External SOPs can be accessed through:

1. **Gateway Lambda Functions**: Deploy custom Lambda functions that fetch SOPs from external sources
2. **MCP Server Tools**: Use MCP servers to access git repositories, APIs, or databases
3. **Dynamic Loading**: Agent queries external sources based on context and caches results

## Sample Queries

Try these queries with the agent:

1. "What SOPs are available?"
2. "I need to admit a cardiac patient to ICU"
3. "Emergency code blue situation"
4. "How do I safely administer medications?"
5. "Show me the patient admission process"
6. "Start SOP-CARD-001"
7. "Complete this step"
8. "What's my current progress?"

## Cleanup

```bash
chmod +x scripts/cleanup.sh
./scripts/cleanup.sh

python scripts/cognito_credentials_provider.py delete
python scripts/agentcore_memory.py delete
python scripts/agentcore_gateway.py delete
python scripts/agentcore_agent_runtime.py myappDynamicSOPAgent

rm .agentcore.yaml
rm .bedrock_agentcore.yaml
```

## Differences from Standalone Dynamic SOP Agent

This agent (35-AgentCore-Dynamic-SOP-Agent) differs from the standalone Dynamic SOP Agent (34-Dynamic-SOP-Agent) in:

1. **Enterprise Deployment**: Integrated with AgentCore for production deployment
2. **Authentication**: Supports OAuth and IAM authentication
3. **Memory System**: Integrated conversation memory and preferences
4. **Gateway Integration**: Access to Lambda-based tools and external systems
5. **UI**: Streamlit-based web interface included
6. **Observability**: CloudWatch integration for monitoring
7. **Scalability**: Designed for multi-user enterprise environments

## Troubleshooting

### No SOPs Loaded
```bash
# Verify SOP directory exists
ls examples/sops/

# Check SOP file format (valid JSON/YAML)
python -m json.tool examples/sops/patient_admission.json
```

### Gateway Connection Failed
```bash
# Verify gateway is created
python scripts/agentcore_gateway.py create --name myapp-gw

# Check SSM parameters
./scripts/list_ssm_parameters.sh
```

### Authentication Issues
```bash
# Verify Cognito setup
python scripts/cognito_credentials_provider.py create --name myapp-cp

# Test gateway access
python tests/test_gateway.py --prompt "Hello"
```

## Contributing

Contributions are welcome! To add new features:

1. Add new SOP categories in `context_analyzer.py`
2. Create example SOPs in `examples/sops/`
3. Add new tools in `tools/sop_tools.py`
4. Update tests and documentation
5. Submit pull request with detailed description

## License

See [LICENSE](../../LICENSE) file in repository root.

## Support

For issues or questions:
- Review this README and setup instructions
- Check example SOPs in `examples/sops/`
- Run test suite to verify installation
- Review AgentCore template documentation
- Open GitHub issue with details

## Version History

- **v1.0.0** (2024-12-10): Initial release
  - Context-aware SOP discovery
  - Multi-source SOP loading
  - AgentCore integration
  - Step-by-step execution tracking
  - OAuth and IAM authentication
  - Streamlit UI
  - Example SOPs for healthcare workflows
