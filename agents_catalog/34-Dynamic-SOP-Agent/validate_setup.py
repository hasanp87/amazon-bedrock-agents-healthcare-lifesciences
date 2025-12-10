#!/usr/bin/env python3
"""
Validation script to verify the Dynamic SOP Agent setup is complete
"""

import os
import sys
import json


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False


def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if os.path.isdir(dirpath):
        file_count = len([f for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))])
        print(f"✅ {description}: {dirpath} ({file_count} files)")
        return True
    else:
        print(f"❌ {description} MISSING: {dirpath}")
        return False


def validate_json_file(filepath):
    """Validate JSON file syntax"""
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return True
    except Exception as e:
        print(f"   ⚠️  JSON validation warning: {e}")
        return False


def main():
    """Run validation checks"""
    print("=" * 70)
    print("  DYNAMIC SOP AGENT - SETUP VALIDATION")
    print("=" * 70)
    print()
    
    all_checks_passed = True
    
    # Check core files
    print("📄 Core Files:")
    all_checks_passed &= check_file_exists("README.md", "README")
    all_checks_passed &= check_file_exists("SETUP.md", "Setup Guide")
    all_checks_passed &= check_file_exists("requirements.txt", "Requirements")
    all_checks_passed &= check_file_exists("main.py", "Main Application")
    all_checks_passed &= check_file_exists("demo.py", "Demo Script")
    print()
    
    # Check source directories
    print("📁 Source Code Structure:")
    all_checks_passed &= check_directory_exists("src", "Source Directory")
    all_checks_passed &= check_directory_exists("src/agents", "Agents Directory")
    all_checks_passed &= check_directory_exists("src/agents/tools", "Tools Directory")
    all_checks_passed &= check_directory_exists("src/models", "Models Directory")
    all_checks_passed &= check_directory_exists("src/utils", "Utils Directory")
    print()
    
    # Check key source files
    print("🐍 Python Modules:")
    all_checks_passed &= check_file_exists("src/__init__.py", "Package Init")
    all_checks_passed &= check_file_exists("src/agents/dynamic_sop_agent.py", "Main Agent")
    all_checks_passed &= check_file_exists("src/models/sop_models.py", "Data Models")
    all_checks_passed &= check_file_exists("src/utils/sop_loader.py", "SOP Loader")
    all_checks_passed &= check_file_exists("src/utils/context_analyzer.py", "Context Analyzer")
    all_checks_passed &= check_file_exists("src/utils/mcp_connector.py", "MCP Connector")
    print()
    
    # Check tools
    print("🔧 Agent Tools:")
    all_checks_passed &= check_file_exists("src/agents/tools/sop_retrieval.py", "SOP Retrieval")
    all_checks_passed &= check_file_exists("src/agents/tools/sop_application.py", "SOP Application")
    all_checks_passed &= check_file_exists("src/agents/tools/context_tools.py", "Context Tools")
    print()
    
    # Check tests
    print("🧪 Test Suite:")
    all_checks_passed &= check_directory_exists("tests", "Tests Directory")
    all_checks_passed &= check_file_exists("tests/test_models.py", "Model Tests")
    all_checks_passed &= check_file_exists("tests/test_context_analyzer.py", "Context Tests")
    all_checks_passed &= check_file_exists("tests/test_sop_loader.py", "Loader Tests")
    print()
    
    # Check examples
    print("📚 Example SOPs:")
    all_checks_passed &= check_directory_exists("examples/sops", "Examples Directory")
    
    sop_files = [
        "examples/sops/patient_admission.json",
        "examples/sops/emergency_response.yaml",
        "examples/sops/medication_administration.json"
    ]
    
    for sop_file in sop_files:
        if check_file_exists(sop_file, f"Example SOP"):
            if sop_file.endswith('.json'):
                validate_json_file(sop_file)
    print()
    
    # Check configuration
    print("⚙️  Configuration:")
    all_checks_passed &= check_directory_exists("config", "Config Directory")
    all_checks_passed &= check_file_exists("config/mcp_config_example.json", "MCP Config Example")
    print()
    
    # Run basic import test
    print("🔍 Import Tests:")
    try:
        from src.models.sop_models import SOP, SOPStep, SOPMetadata
        print("✅ Data models import successfully")
    except Exception as e:
        print(f"❌ Data models import failed: {e}")
        all_checks_passed = False
    
    try:
        from src.utils.context_analyzer import ContextAnalyzer
        print("✅ Context analyzer imports successfully")
    except Exception as e:
        print(f"❌ Context analyzer import failed: {e}")
        all_checks_passed = False
    
    try:
        from src.utils.sop_loader import SOPLoader
        print("✅ SOP loader imports successfully")
    except Exception as e:
        print(f"❌ SOP loader import failed: {e}")
        all_checks_passed = False
    print()
    
    # Summary
    print("=" * 70)
    if all_checks_passed:
        print("✅ ALL VALIDATION CHECKS PASSED")
        print()
        print("🎉 Dynamic SOP Agent is ready to use!")
        print()
        print("Next steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run tests: python3 tests/test_models.py")
        print("  3. Try demo: python3 demo.py")
        print("  4. Run agent: python3 main.py")
    else:
        print("❌ SOME VALIDATION CHECKS FAILED")
        print()
        print("Please review the errors above and fix any missing files or imports.")
        sys.exit(1)
    print("=" * 70)


if __name__ == "__main__":
    main()
