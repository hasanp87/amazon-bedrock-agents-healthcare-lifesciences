"""
Test SOP Loader functionality
"""

import sys
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

from agent_config.sop_loader import SOPLoader


def test_load_from_directory():
    """Test loading SOPs from examples directory"""
    print("Testing SOP Loader...\n")
    
    loader = SOPLoader()
    examples_dir = Path(__file__).parent.parent / "examples" / "sops"
    
    if not examples_dir.exists():
        print(f"❌ Examples directory not found: {examples_dir}")
        return False
    
    try:
        repo = loader.load_from_directory(str(examples_dir), "test_repo")
        
        print(f"\n✅ Successfully loaded {len(repo.sops)} SOPs")
        print(f"\nRepository Summary:")
        print(f"  Name: {repo.name}")
        print(f"  Source: {repo.source_type}")
        print(f"  Categories: {', '.join(repo.get_all_categories())}")
        
        print(f"\n📋 Loaded SOPs:")
        for sop in repo.sops:
            print(f"  • {sop.id}: {sop.title}")
            print(f"    Category: {sop.category}, Priority: {sop.priority}")
            print(f"    Steps: {len(sop.steps)}, Departments: {', '.join(sop.applicable_departments)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading SOPs: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sop_details():
    """Test retrieving SOP details"""
    print("\n\nTesting SOP Details Retrieval...\n")
    
    loader = SOPLoader()
    examples_dir = Path(__file__).parent.parent / "examples" / "sops"
    
    try:
        repo = loader.load_from_directory(str(examples_dir), "test_repo")
        
        # Get first SOP
        if repo.sops:
            sop = repo.sops[0]
            print(f"📄 SOP Details: {sop.id}")
            print(f"   Title: {sop.title}")
            print(f"   Description: {sop.description}")
            print(f"   Category: {sop.category}")
            print(f"   Priority: {sop.priority}")
            print(f"   Total Steps: {len(sop.steps)}")
            
            if sop.steps:
                print(f"\n   First Step:")
                step = sop.steps[0]
                print(f"     {step.step_number}. {step.description}")
                if step.details:
                    print(f"     Details: {step.details[:100]}...")
                if step.warnings:
                    print(f"     Warnings: {step.warnings[0]}")
            
            print(f"\n   Metadata:")
            print(f"     Version: {sop.metadata.version}")
            print(f"     Author: {sop.metadata.author}")
            print(f"     Status: {sop.metadata.approval_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("SOP Loader Test Suite")
    print("=" * 60)
    
    success = True
    success = test_load_from_directory() and success
    success = test_sop_details() and success
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
