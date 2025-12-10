# Dynamic SOP Agent - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
conda create -n dynamic-sop python=3.11 -y
conda activate dynamic-sop
pip install -r requirements.txt
```

### 2. Run the Agent
```bash
python3 main.py
```

### 3. Try These Commands
```
💬 You: I need to admit a cardiac patient to ICU
💬 You: search for emergency
💬 You: list all sops
💬 You: start sop SOP-CARD-001
💬 You: complete step 1
💬 You: status
💬 You: help
```

## 📚 Example SOPs Included

1. **SOP-CARD-001**: Cardiac ICU Patient Admission
2. **SOP-EMRG-001**: Emergency Code Blue Response  
3. **SOP-PHARM-001**: Safe Medication Administration

## 🎯 Common Use Cases

### Find Relevant SOPs
```
I need to [describe your task]
Examples:
- "I need to admit a patient"
- "Emergency cardiac arrest"
- "Administering IV medications"
```

### Execute an SOP
```
start sop [SOP-ID]
complete step [N]
get step [N] details
status
```

### Search SOPs
```
search for [keyword]
list all sops
categories
```

## 🔧 Key Features

✅ Context-aware SOP discovery
✅ Step-by-step execution guidance
✅ Progress tracking
✅ Multi-source SOP loading
✅ MCP server integration

## 📖 Full Documentation

- **README.md** - Complete documentation
- **SETUP.md** - Detailed setup and deployment
- **IMPLEMENTATION_NOTES.md** - Technical details

## 🧪 Run Tests
```bash
python3 tests/test_models.py
```

## 🆘 Need Help?
```
Type 'help' in the agent
Read README.md for full documentation
Check SETUP.md for troubleshooting
```

## 📞 Commands Reference

| Command | Description |
|---------|-------------|
| `help` | Show help message |
| `status` | Show active SOP progress |
| `categories` | List SOP categories |
| `repos` | Show loaded repositories |
| `quit` | Exit the agent |

---

**Ready to get started?** Run `python3 main.py` now! 🎉
