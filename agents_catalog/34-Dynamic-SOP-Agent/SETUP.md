# Setup and Deployment Guide

## Quick Setup (5 minutes)

### 1. Environment Setup

```bash
# Create conda environment
conda create -n dynamic-sop python=3.11 -y
conda activate dynamic-sop

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
# Run tests
python3 tests/test_models.py

# Check example SOPs loaded
python3 -c "import json; print(json.load(open('examples/sops/patient_admission.json'))['title'])"
```

### 3. Run Demo

```bash
# Interactive demo
python3 demo.py

# Or run main application
python3 main.py
```

## Advanced Setup with MCP Servers

### Prerequisites for MCP Integration

1. **Python 3.8+** with pip and uvx installed
2. **AWS Credentials** configured (`aws configure`)
3. **GitHub Token** (for Git repository access)
4. **MCP Client** (e.g., Amazon Q Developer CLI)

### Installing MCP Servers

```bash
# Install uvx if not already installed
pip install uvx

# Install MCP servers
uvx install awslabs.git-repo-research-mcp-server@latest
uvx install awslabs.aws-documentation-mcp-server@latest
uvx install awslabs.cfn-mcp-server@latest
```

### Configuring MCP Servers

1. **Copy example configuration:**
```bash
cp config/mcp_config_example.json ~/.amazonq/mcp.json
```

2. **Edit configuration:**
```bash
nano ~/.amazonq/mcp.json
```

3. **Replace placeholders:**
   - `YOUR_GITHUB_TOKEN` - Your GitHub personal access token
   - `YOUR_AWS_PROFILE` - Your AWS CLI profile name
   - Adjust AWS region if needed

### Verifying MCP Setup

```bash
# Check MCP servers are available
uvx awslabs.git-repo-research-mcp-server@latest --help
uvx awslabs.aws-documentation-mcp-server@latest --help
```

## Using MCP Servers in Code

### Example 1: Load SOPs from Git Repository

```python
from src.agents.dynamic_sop_agent import DynamicSOPAgent

agent = DynamicSOPAgent()

# Connect to Git repository via MCP
agent.mcp_connector.connect_git_repo_mcp(
    repo_name="hospital_sops",
    repo_url="https://github.com/your-org/sop-repository",
    sop_path="procedures"
)

# Load SOPs (uses local cache if available)
sops = agent.mcp_connector.load_sops_from_repository(
    "hospital_sops",
    local_cache_path="cached_sops/hospital"
)

print(f"Loaded {len(sops)} SOPs from repository")
```

### Example 2: Access AWS Service SOPs

```python
# Connect to AWS Documentation
agent.mcp_connector.connect_aws_docs_mcp(
    service_names=["bedrock", "healthlake", "comprehendmedical"]
)

# Access service-specific SOPs
agent.chat("Show me SOPs for using Amazon Bedrock")
```

### Example 3: Custom MCP Server

```python
# Connect to custom internal server
agent.mcp_connector.connect_custom_mcp(
    name="internal_hospital_sops",
    mcp_config={
        "source_url": "https://internal.hospital.com/sops",
        "api_key": os.environ.get("HOSPITAL_API_KEY"),
        "description": "Internal hospital SOPs"
    }
)
```

## Deployment Options

### Option 1: Local Development

Run directly on your machine:
```bash
python3 main.py
```

### Option 2: Streamlit Web App

Create a web interface (requires streamlit):
```bash
pip install streamlit

# Create app.py:
# import streamlit as st
# from src.agents.dynamic_sop_agent import DynamicSOPAgent
# 
# st.title("Dynamic SOP Assistant")
# agent = DynamicSOPAgent(sop_directories=["examples/sops"])
# 
# user_input = st.text_input("Ask about SOPs:")
# if user_input:
#     response = agent.chat(user_input)
#     st.write(response)

streamlit run app.py
```

### Option 3: AWS Lambda Function

Deploy as serverless function:
```python
# lambda_handler.py
import json
from src.agents.dynamic_sop_agent import DynamicSOPAgent

agent = None

def lambda_handler(event, context):
    global agent
    if agent is None:
        agent = DynamicSOPAgent(sop_directories=["/tmp/sops"])
    
    user_message = json.loads(event['body'])['message']
    response = agent.chat(user_message)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'response': response})
    }
```

### Option 4: Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
```

Build and run:
```bash
docker build -t dynamic-sop-agent .
docker run -it dynamic-sop-agent
```

### Option 5: API Server

Create a REST API (requires fastapi):
```bash
pip install fastapi uvicorn

# Create api.py:
# from fastapi import FastAPI
# from src.agents.dynamic_sop_agent import DynamicSOPAgent
# 
# app = FastAPI()
# agent = DynamicSOPAgent(sop_directories=["examples/sops"])
# 
# @app.post("/chat")
# async def chat(message: str):
#     response = agent.chat(message)
#     return {"response": response}

uvicorn api:app --reload
```

## Configuration Management

### Environment Variables

Set these environment variables for customization:

```bash
export SOP_DIRECTORY="examples/sops"
export AWS_PROFILE="default"
export AWS_REGION="us-east-1"
export GITHUB_TOKEN="your-token"
export LOG_LEVEL="INFO"
```

### Configuration File

Edit `config/mcp_config_example.json` to customize:

- MCP server connections
- SOP repository sources
- Context analysis settings
- Agent behavior parameters

## Troubleshooting

### Issue: Module 'strands' not found

**Solution:**
```bash
pip install strands-agents
# Or if in conda environment:
conda install -c conda-forge strands-agents
```

### Issue: MCP server connection fails

**Solution:**
1. Verify MCP server is installed: `uvx list`
2. Check credentials are set correctly
3. Test MCP server independently: `uvx awslabs.git-repo-research-mcp-server@latest --test`

### Issue: No SOPs loaded

**Solution:**
1. Check directory path exists: `ls -la examples/sops/`
2. Verify JSON/YAML syntax: `python3 -m json.tool examples/sops/patient_admission.json`
3. Check file permissions: `chmod 644 examples/sops/*.json`

### Issue: Context not detected correctly

**Solution:**
1. Use more specific language in queries
2. Manually set context: `agent.chat("set context department=cardiology")`
3. Check context keywords: `agent.chat("list context keywords")`

### Issue: AWS credentials not found

**Solution:**
```bash
aws configure
# Enter your credentials when prompted
```

## Performance Optimization

### Caching

Enable SOP caching to improve load times:
```python
agent.mcp_connector.load_sops_from_repository(
    "repo_name",
    local_cache_path="cached_sops"  # Caches SOPs locally
)
```

### Batch Loading

Load multiple repositories at once:
```python
repositories = [
    ("local_sops", "local", "examples/sops"),
    ("git_sops", "mcp_git", "https://github.com/org/sops"),
]

for name, source_type, source_url in repositories:
    agent.register_mcp_repository(name, source_type, source_url)
```

## Security Considerations

### API Keys and Tokens

Never commit sensitive credentials:
```bash
# Use environment variables
export GITHUB_TOKEN="your-token"

# Or use AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id github-token
```

### Access Control

Implement role-based access:
```python
def check_user_permission(user_role, sop):
    """Verify user has permission to access SOP"""
    return user_role in sop.applicable_roles
```

### Audit Logging

Log all SOP access:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sop_agent")

def log_sop_access(user, sop_id):
    logger.info(f"User {user} accessed SOP {sop_id}")
```

## Monitoring and Maintenance

### Health Checks

```python
def health_check():
    """Verify agent is functioning"""
    agent = DynamicSOPAgent()
    sops = agent.mcp_connector.get_all_sops()
    return len(sops) > 0
```

### Update SOPs Regularly

```bash
# Sync SOPs from repositories
python3 -c "
from src.agents.dynamic_sop_agent import DynamicSOPAgent
agent = DynamicSOPAgent()
# Sync all repositories
for repo_name in agent.mcp_connector.list_repositories():
    count = agent.mcp_connector.sync_repository(repo_name)
    print(f'Synced {count} SOPs from {repo_name}')
"
```

## Next Steps

1. **Customize SOPs**: Add your organization's SOPs to `examples/sops/`
2. **Configure MCP**: Set up MCP servers for external SOP sources
3. **Deploy**: Choose deployment option based on your needs
4. **Integrate**: Connect to your EHR or workflow systems
5. **Monitor**: Set up logging and monitoring for production use

## Support

For issues or questions:
- Check README.md for detailed documentation
- Run test suite: `python3 tests/test_models.py`
- Review example SOPs in `examples/sops/`
- Open GitHub issue with details
