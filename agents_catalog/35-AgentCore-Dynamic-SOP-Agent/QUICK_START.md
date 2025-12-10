# Quick Start Guide - AgentCore Dynamic SOP Agent

This guide will help you quickly get started with the AgentCore Dynamic SOP Agent.

## Quick Test (Without Full Deployment)

To quickly test the SOP loading and context analysis without deploying to AgentCore:

### 1. Install Dependencies

```bash
cd agents_catalog/35-AgentCore-Dynamic-SOP-Agent
python -m venv .venv
source .venv/bin/activate
pip install PyYAML pydantic
```

### 2. Run Tests

```bash
# Test SOP loading from examples
python tests/test_sop_loader.py

# Test context analysis
python tests/test_context_analyzer.py
```

Expected output:
```
✅ Successfully loaded 3 SOPs
📋 Loaded SOPs:
  • SOP-CARD-001: Cardiac ICU Patient Admission Protocol
  • SOP-EMRG-001: Emergency Code Blue Response Protocol
  • SOP-PHARM-001: Safe Medication Administration Protocol
```

## Full Deployment to AgentCore

### Prerequisites Checklist

- [ ] AWS account with appropriate permissions
- [ ] AWS CLI configured (`aws configure`)
- [ ] Python 3.10 or higher installed
- [ ] Bedrock model access enabled (Claude 3.7 Sonnet)
- [ ] Chosen resource prefix (e.g., "myapp")

### Step-by-Step Deployment

#### 1. Clone and Navigate

```bash
cd /path/to/agents_catalog/35-AgentCore-Dynamic-SOP-Agent
```

#### 2. Setup Python Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r dev-requirements.txt
```

#### 3. Deploy Infrastructure (10-15 minutes)

```bash
chmod +x scripts/prereq.sh
./scripts/prereq.sh
```

When prompted, use your prefix (e.g., `myapp`) for all resource names.

#### 4. Verify Infrastructure

```bash
chmod +x scripts/list_ssm_parameters.sh
./scripts/list_ssm_parameters.sh
```

Save the output - you'll need these parameter values later.

#### 5. Create Gateway (2-3 minutes)

```bash
python scripts/agentcore_gateway.py create --name myapp-gw
```

#### 6. Setup Authentication (2-3 minutes)

```bash
python scripts/cognito_credentials_provider.py create --name myapp-cp
```

#### 7. Create Memory (1-2 minutes)

```bash
python scripts/agentcore_memory.py create --name myapp
```

#### 8. Configure and Deploy Agent (5-7 minutes)

```bash
# Configure
agentcore configure \
  --entrypoint main.py \
  -rf agent/requirements.txt \
  -er arn:aws:iam::<YOUR-ACCOUNT-ID>:role/<YOUR-ROLE> \
  --name myappDynamicSOPAgent
```

Replace:
- `<YOUR-ACCOUNT-ID>`: Your AWS account ID
- `<YOUR-ROLE>`: Role name from SSM parameter `/app/myapp/agentcore/runtime_iam_role`

When prompted:
- OAuth? Choose based on your needs (yes for OAuth, no for IAM)
- OAuth Discovery URL: Get from `/app/myapp/agentcore/cognito_discovery_url`
- OAuth Client ID: Get from `/app/myapp/agentcore/web_client_id`

```bash
# Deploy
rm .agentcore.yaml  # Clean up before launch
agentcore launch
```

#### 9. Test the Agent

**Option A: CLI Test (IAM)**
```bash
agentcore invoke '{"prompt": "What SOPs are available?"}'
```

**Option B: CLI Test (OAuth)**
```bash
python tests/test_agent.py myappDynamicSOPAgent -p "What SOPs are available?"
```

**Option C: Streamlit UI (IAM)**
```bash
streamlit run app.py --server.port 8501
```

**Option D: Streamlit UI (OAuth)**
```bash
streamlit run app_oauth.py --server.port 8501 -- --agent=myappDynamicSOPAgent
```

### First Interactions

Try these queries once the agent is running:

1. **List Available SOPs**
   ```
   What SOPs are available?
   ```

2. **Context-Based Search**
   ```
   I need to admit a cardiac patient to ICU
   ```

3. **Emergency Scenario**
   ```
   Emergency code blue in room 301
   ```

4. **Get Specific SOP**
   ```
   Show me details of SOP-CARD-001
   ```

5. **Start SOP Execution**
   ```
   Start SOP-CARD-001
   ```

6. **Complete Steps**
   ```
   Complete this step with note: Patient identified and verified
   ```

7. **Check Progress**
   ```
   What's my current progress?
   ```

## Expected Response Examples

### Listing SOPs
```
📚 Available SOPs (3 total):

CLINICAL (2 SOPs):
  • SOP-CARD-001: Cardiac ICU Patient Admission Protocol (high priority)
  • SOP-PHARM-001: Safe Medication Administration Protocol (high priority)

SAFETY (1 SOP):
  • SOP-EMRG-001: Emergency Code Blue Response Protocol (critical priority)
```

### Context-Based Search
```
🎯 Relevant SOPs for: 'I need to admit a cardiac patient to ICU'

Detected context:
  • Category: clinical
  • Department: cardiology
  • Task: admission
  • Priority: high

📋 Top matching SOPs:

1. SOP-CARD-001: Cardiac ICU Patient Admission Protocol (relevance: 23.0)
   Category: clinical | Priority: high
   Standard procedure for admitting patients to the Cardiac Intensive Care Unit
   Departments: cardiology, icu, emergency
```

### Starting SOP
```
✅ Started SOP: SOP-CARD-001 - Cardiac ICU Patient Admission Protocol

Total Steps: 6
Priority: high

📋 Prerequisites:
  • Physician order for ICU admission
  • ICU bed availability confirmed
  • Patient consent obtained

📍 Current Step: 1/6

Step 1: Verify physician orders and patient identification
Details: Review admission orders, confirm patient identity...
Estimated Time: 5 minutes

Validation Criteria:
  ✓ Patient identity confirmed with two identifiers
  ✓ Admission orders signed by attending physician
  ✓ Diagnosis documented in chart

⚠️ Warnings:
  • Do not proceed without proper identification verification
```

## Adding Your Own SOPs

### 1. Create SOP File

Create a new JSON file in `examples/sops/`:

```json
{
  "id": "SOP-YOUR-001",
  "title": "Your SOP Title",
  "description": "Brief description",
  "category": "clinical",
  "priority": "high",
  "applicable_departments": ["your-dept"],
  "applicable_roles": ["your-role"],
  "keywords": ["keyword1", "keyword2"],
  "steps": [
    {
      "step_number": 1,
      "description": "First step",
      "required": true,
      "estimated_time": "5 minutes"
    }
  ],
  "metadata": {
    "version": "1.0",
    "created_date": "2024-12-10",
    "last_updated": "2024-12-10",
    "author": "Your Name",
    "approval_status": "draft"
  }
}
```

### 2. Restart Agent

```bash
# If running locally
python tests/test_sop_loader.py

# If deployed to AgentCore
agentcore launch  # Redeploy
```

### 3. Verify SOP Loaded

```
User: What SOPs are available?
Agent: [Should list your new SOP]
```

## Troubleshooting

### SOPs Not Loading
```bash
# Check if files are valid JSON/YAML
python -m json.tool examples/sops/your_sop.json

# Run loader test
python tests/test_sop_loader.py
```

### Gateway Connection Issues
```bash
# Verify gateway exists
aws lambda list-functions | grep myapp-gw

# Recreate gateway
python scripts/agentcore_gateway.py delete
python scripts/agentcore_gateway.py create --name myapp-gw
```

### Agent Not Responding
```bash
# Check logs
aws logs tail /aws/lambda/myappDynamicSOPAgent --follow

# Verify runtime exists
agentcore list
```

### Memory Issues
```bash
# Verify memory exists
python tests/test_memory.py list-memory

# Recreate memory
python scripts/agentcore_memory.py delete
python scripts/agentcore_memory.py create --name myapp
```

## Next Steps

1. **Add Custom SOPs**: Create your organization's SOPs in `examples/sops/`
2. **Configure MCP Servers**: Connect to external SOP repositories (see README.md)
3. **Customize Context Rules**: Modify `context_analyzer.py` for your domain
4. **Add Custom Tools**: Extend agent capabilities in `tools/sop_tools.py`
5. **Setup Monitoring**: Configure CloudWatch dashboards for observability
6. **Train Users**: Share sample queries and best practices with your team

## Support

- 📖 Full documentation: See [README.md](README.md)
- 🧪 Run tests: `python tests/test_*.py`
- 🔍 Check logs: AWS CloudWatch or local console
- 📝 Example SOPs: `examples/sops/`
- 🛠️ AgentCore docs: [AgentCore Template README](../../agentcore_template/README.md)

## Estimated Time

- Quick test (no deployment): **5 minutes**
- Full deployment: **30-40 minutes**
- Adding custom SOPs: **5-10 minutes per SOP**

Enjoy using the AgentCore Dynamic SOP Agent! 🚀
