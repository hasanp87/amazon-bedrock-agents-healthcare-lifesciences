"""
Tests for SOP Loader
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.sop_loader import SOPLoader


def test_load_json_sop():
    """Test loading SOP from JSON file"""
    loader = SOPLoader()
    
    sop_file = "examples/sops/patient_admission.json"
    
    if not os.path.exists(sop_file):
        print(f"⚠️  Skipping test: {sop_file} not found")
        return
    
    print("Test: Load SOP from JSON")
    sop = loader.load_from_json(sop_file)
    
    print(f"SOP ID: {sop.id}")
    print(f"Title: {sop.title}")
    print(f"Category: {sop.category}")
    print(f"Steps: {len(sop.steps)}")
    print(f"Keywords: {sop.keywords}")
    
    assert sop.id == "SOP-CARD-001", "Should load correct SOP ID"
    assert len(sop.steps) == 6, "Should load all 6 steps"
    assert sop.category == "clinical", "Should have clinical category"
    print("✅ PASSED\n")


def test_load_yaml_sop():
    """Test loading SOP from YAML file"""
    loader = SOPLoader()
    
    sop_file = "examples/sops/emergency_response.yaml"
    
    if not os.path.exists(sop_file):
        print(f"⚠️  Skipping test: {sop_file} not found")
        return
    
    print("Test: Load SOP from YAML")
    sop = loader.load_from_yaml(sop_file)
    
    print(f"SOP ID: {sop.id}")
    print(f"Title: {sop.title}")
    print(f"Category: {sop.category}")
    print(f"Priority: {sop.priority}")
    print(f"Steps: {len(sop.steps)}")
    
    assert sop.id == "SOP-EMRG-001", "Should load correct SOP ID"
    assert sop.priority == "critical", "Should have critical priority"
    assert len(sop.steps) == 8, "Should load all 8 steps"
    print("✅ PASSED\n")


def test_load_directory():
    """Test loading all SOPs from a directory"""
    loader = SOPLoader()
    
    sop_dir = "examples/sops"
    
    if not os.path.exists(sop_dir):
        print(f"⚠️  Skipping test: {sop_dir} not found")
        return
    
    print("Test: Load SOPs from Directory")
    repository = loader.load_directory(sop_dir)
    
    print(f"Repository: {repository.name}")
    print(f"SOPs loaded: {len(repository.sops)}")
    print(f"Categories: {repository.get_all_categories()}")
    
    assert len(repository.sops) >= 2, "Should load multiple SOPs"
    assert "clinical" in repository.get_all_categories(), "Should have clinical category"
    
    for sop in repository.sops:
        print(f"  • {sop.id}: {sop.title}")
    
    print("✅ PASSED\n")


def test_sop_step_parsing():
    """Test that SOP steps are parsed correctly"""
    loader = SOPLoader()
    
    sop_file = "examples/sops/patient_admission.json"
    
    if not os.path.exists(sop_file):
        print(f"⚠️  Skipping test: {sop_file} not found")
        return
    
    print("Test: SOP Step Parsing")
    sop = loader.load_from_json(sop_file)
    
    first_step = sop.steps[0]
    print(f"Step {first_step.step_number}: {first_step.description}")
    print(f"Required: {first_step.required}")
    print(f"Warnings: {first_step.warnings}")
    print(f"Validation criteria: {len(first_step.validation_criteria) if first_step.validation_criteria else 0}")
    
    assert first_step.step_number == 1, "First step should be numbered 1"
    assert first_step.required is True, "Step should be marked as required"
    assert first_step.warnings is not None, "Step should have warnings"
    print("✅ PASSED\n")


def test_sop_metadata_parsing():
    """Test that SOP metadata is parsed correctly"""
    loader = SOPLoader()
    
    sop_file = "examples/sops/medication_administration.json"
    
    if not os.path.exists(sop_file):
        print(f"⚠️  Skipping test: {sop_file} not found")
        return
    
    print("Test: SOP Metadata Parsing")
    sop = loader.load_from_json(sop_file)
    
    metadata = sop.metadata
    print(f"Version: {metadata.version}")
    print(f"Author: {metadata.author}")
    print(f"Approval Status: {metadata.approval_status}")
    print(f"Review Frequency: {metadata.review_frequency}")
    
    assert metadata.version is not None, "Should have version"
    assert metadata.approval_status == "approved", "Should be approved"
    print("✅ PASSED\n")


def run_all_tests():
    """Run all SOP loader tests"""
    print("=" * 60)
    print("SOP LOADER TESTS")
    print("=" * 60)
    print()
    
    test_load_json_sop()
    test_load_yaml_sop()
    test_load_directory()
    test_sop_step_parsing()
    test_sop_metadata_parsing()
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
