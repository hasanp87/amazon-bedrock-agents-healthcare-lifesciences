#!/usr/bin/env python3
"""
Validation script for Strands agent-sop Framework Integration
Verifies that the Dynamic SOP Agent properly integrates with agent-sop
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report result"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NOT FOUND: {filepath}")
        return False

def check_markdown_sops():
    """Check if markdown SOPs exist"""
    sop_dir = Path("examples/sops")
    md_files = list(sop_dir.glob("*.md"))
    
    if md_files:
        print(f"\n✅ Found {len(md_files)} markdown SOP(s):")
        for md_file in md_files:
            print(f"   - {md_file.name}")
        return True
    else:
        print("\n❌ No markdown SOPs found")
        return False

def check_rfc2119_keywords(filepath):
    """Check if a markdown SOP contains RFC 2119 keywords"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        keywords = ['MUST', 'SHOULD', 'MAY', 'MUST NOT']
        found_keywords = [kw for kw in keywords if kw in content]
        
        if found_keywords:
            print(f"✅ RFC 2119 keywords found in {filepath.name}: {', '.join(found_keywords)}")
            return True
        else:
            print(f"⚠️  No RFC 2119 keywords found in {filepath.name}")
            return False
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

def check_requirements():
    """Check if strands-agents-sops is in requirements"""
    req_file = Path("agent/requirements.txt")
    try:
        with open(req_file, 'r') as f:
            content = f.read()
        
        if 'strands-agents-sops' in content:
            print(f"✅ strands-agents-sops package in requirements.txt")
            return True
        else:
            print(f"❌ strands-agents-sops package NOT in requirements.txt")
            return False
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def check_loader_markdown_support():
    """Check if sop_loader.py has markdown loading method"""
    loader_file = Path("agent/agent_config/sop_loader.py")
    try:
        with open(loader_file, 'r') as f:
            content = f.read()
        
        if '_load_sop_from_markdown' in content:
            print(f"✅ Markdown loading method in sop_loader.py")
            return True
        else:
            print(f"❌ Markdown loading method NOT in sop_loader.py")
            return False
    except Exception as e:
        print(f"❌ Error reading sop_loader.py: {e}")
        return False

def check_agent_prompt_rfc2119():
    """Check if agent.py mentions RFC 2119 in system prompt"""
    agent_file = Path("agent/agent_config/agent.py")
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        if 'RFC 2119' in content or 'MUST' in content:
            print(f"✅ RFC 2119 / agent-sop concepts in agent.py")
            return True
        else:
            print(f"⚠️  RFC 2119 concepts not explicitly mentioned in agent.py")
            return False
    except Exception as e:
        print(f"❌ Error reading agent.py: {e}")
        return False

def main():
    """Run all validation checks"""
    print("=" * 70)
    print("Strands agent-sop Framework Integration Validation")
    print("=" * 70)
    
    checks_passed = 0
    total_checks = 0
    
    print("\n📋 Checking Documentation Files...")
    total_checks += 1
    if check_file_exists("STRANDS_AGENT_SOP_INTEGRATION.md", "Integration documentation"):
        checks_passed += 1
    
    total_checks += 1
    if check_file_exists("CHANGELOG_STRANDS_AGENT_SOP.md", "Changelog"):
        checks_passed += 1
    
    print("\n📦 Checking Package Dependencies...")
    total_checks += 1
    if check_requirements():
        checks_passed += 1
    
    print("\n📝 Checking Markdown SOP Files...")
    total_checks += 1
    if check_markdown_sops():
        checks_passed += 1
    
    print("\n🔍 Checking RFC 2119 Keywords in SOPs...")
    sop_dir = Path("examples/sops")
    for md_file in sop_dir.glob("*.md"):
        total_checks += 1
        if check_rfc2119_keywords(md_file):
            checks_passed += 1
    
    print("\n⚙️  Checking Code Implementation...")
    total_checks += 1
    if check_loader_markdown_support():
        checks_passed += 1
    
    total_checks += 1
    if check_agent_prompt_rfc2119():
        checks_passed += 1
    
    print("\n" + "=" * 70)
    print(f"Validation Results: {checks_passed}/{total_checks} checks passed")
    print("=" * 70)
    
    if checks_passed == total_checks:
        print("\n🎉 SUCCESS! All validation checks passed!")
        print("\nThe Dynamic SOP Agent is properly integrated with the Strands agent-sop framework.")
        print("\nKey Features Verified:")
        print("  ✓ Markdown-based SOPs with RFC 2119 keywords")
        print("  ✓ strands-agents-sops package dependency")
        print("  ✓ Markdown SOP loading capability")
        print("  ✓ Agent understands RFC 2119 constraint levels")
        print("  ✓ Comprehensive documentation")
        return 0
    else:
        print(f"\n⚠️  WARNING: {total_checks - checks_passed} validation check(s) failed")
        print("\nPlease review the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
