"""
Test the agent structure and file organization
"""

import os
from pathlib import Path


def test_directory_structure():
    """Test that all required directories exist"""
    print("Testing Directory Structure...\n")
    
    base_dir = Path(__file__).parent.parent
    
    required_dirs = [
        "agent",
        "agent/agent_config",
        "agent/agent_config/tools",
        "examples",
        "examples/sops",
        "tests",
        "scripts",
        "prerequisite",
        "app_modules",
        "config"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - NOT FOUND")
            all_exist = False
    
    return all_exist


def test_required_files():
    """Test that all required files exist"""
    print("\n\nTesting Required Files...\n")
    
    base_dir = Path(__file__).parent.parent
    
    required_files = [
        "main.py",
        "README.md",
        "QUICK_START.md",
        "agent/requirements.txt",
        "agent/agent_config/__init__.py",
        "agent/agent_config/agent.py",
        "agent/agent_config/sop_models.py",
        "agent/agent_config/sop_loader.py",
        "agent/agent_config/context_analyzer.py",
        "agent/agent_config/agent_task.py",
        "agent/agent_config/tools/__init__.py",
        "agent/agent_config/tools/sop_tools.py",
        "examples/sops/patient_admission.json",
        "examples/sops/emergency_response.yaml",
        "examples/sops/medication_administration.json",
        "config/mcp_config_example.json"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist


def test_sop_files():
    """Test that SOP example files are valid"""
    print("\n\nTesting SOP Files...\n")
    
    base_dir = Path(__file__).parent.parent
    sops_dir = base_dir / "examples" / "sops"
    
    if not sops_dir.exists():
        print(f"❌ SOPs directory not found")
        return False
    
    # Count files
    json_files = list(sops_dir.glob("*.json"))
    yaml_files = list(sops_dir.glob("*.yaml")) + list(sops_dir.glob("*.yml"))
    
    print(f"Found {len(json_files)} JSON files:")
    for f in json_files:
        print(f"  • {f.name} ({f.stat().st_size} bytes)")
    
    print(f"\nFound {len(yaml_files)} YAML files:")
    for f in yaml_files:
        print(f"  • {f.name} ({f.stat().st_size} bytes)")
    
    total_sops = len(json_files) + len(yaml_files)
    print(f"\n📊 Total SOPs: {total_sops}")
    
    return total_sops >= 3


def test_code_files():
    """Check that key Python files have content"""
    print("\n\nTesting Code Files Content...\n")
    
    base_dir = Path(__file__).parent.parent
    
    code_checks = {
        "agent/agent_config/agent.py": ["DynamicSOPAgent", "class"],
        "agent/agent_config/sop_models.py": ["SOP", "SOPContext", "dataclass"],
        "agent/agent_config/sop_loader.py": ["SOPLoader", "load_from_directory"],
        "agent/agent_config/context_analyzer.py": ["ContextAnalyzer", "analyze"],
        "agent/agent_config/tools/sop_tools.py": ["search_sops_by_context", "start_sop_execution"]
    }
    
    all_pass = True
    for file_path, keywords in code_checks.items():
        full_path = base_dir / file_path
        if not full_path.exists():
            print(f"❌ {file_path} - NOT FOUND")
            all_pass = False
            continue
        
        content = full_path.read_text()
        found_keywords = [kw for kw in keywords if kw in content]
        
        if len(found_keywords) == len(keywords):
            print(f"✅ {file_path} - Contains: {', '.join(keywords)}")
        else:
            missing = set(keywords) - set(found_keywords)
            print(f"⚠️  {file_path} - Missing: {', '.join(missing)}")
            all_pass = False
    
    return all_pass


if __name__ == "__main__":
    print("=" * 70)
    print("AgentCore Dynamic SOP Agent - Structure Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Required Files", test_required_files),
        ("SOP Files", test_sop_files),
        ("Code Files Content", test_code_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 All tests passed! Agent structure is correct.")
    else:
        print("⚠️  Some tests failed. Please review the output above.")
    print("=" * 70)
    
    exit(0 if all_passed else 1)
