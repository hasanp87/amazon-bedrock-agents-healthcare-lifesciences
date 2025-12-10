"""
Tests for SOP data models (no external dependencies required)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.sop_models import SOP, SOPStep, SOPMetadata, SOPContext, SOPRepository


def test_sop_step_creation():
    """Test creating an SOP step"""
    print("Test: SOPStep Creation")
    
    step = SOPStep(
        step_number=1,
        description="Test step",
        details="Test details",
        required=True,
        validation_criteria=["Criterion 1", "Criterion 2"],
        estimated_time="5 minutes",
        warnings=["Warning 1"]
    )
    
    assert step.step_number == 1
    assert step.description == "Test step"
    assert step.required is True
    assert len(step.validation_criteria) == 2
    
    print(f"  Step number: {step.step_number}")
    print(f"  Description: {step.description}")
    print(f"  Required: {step.required}")
    print("✅ PASSED\n")


def test_sop_metadata():
    """Test SOP metadata"""
    print("Test: SOPMetadata Creation")
    
    metadata = SOPMetadata(
        version="1.0",
        created_date="2024-01-01",
        last_updated="2024-12-10",
        author="Test Author",
        approval_status="approved"
    )
    
    assert metadata.version == "1.0"
    assert metadata.approval_status == "approved"
    
    print(f"  Version: {metadata.version}")
    print(f"  Author: {metadata.author}")
    print(f"  Status: {metadata.approval_status}")
    print("✅ PASSED\n")


def test_sop_creation():
    """Test creating a complete SOP"""
    print("Test: SOP Creation")
    
    step1 = SOPStep(1, "First step", required=True)
    step2 = SOPStep(2, "Second step", required=True)
    
    metadata = SOPMetadata("1.0", "2024-01-01", "2024-01-01", "Author")
    
    sop = SOP(
        id="TEST-001",
        title="Test SOP",
        description="A test SOP",
        category="clinical",
        priority="high",
        steps=[step1, step2],
        metadata=metadata,
        applicable_departments=["test_dept"],
        applicable_roles=["test_role"],
        keywords=["test", "sop"]
    )
    
    assert sop.id == "TEST-001"
    assert len(sop.steps) == 2
    assert sop.category == "clinical"
    assert "test" in sop.keywords
    
    print(f"  SOP ID: {sop.id}")
    print(f"  Title: {sop.title}")
    print(f"  Steps: {len(sop.steps)}")
    print(f"  Category: {sop.category}")
    print("✅ PASSED\n")


def test_sop_get_step():
    """Test retrieving a specific step"""
    print("Test: SOP.get_step()")
    
    steps = [
        SOPStep(1, "First step"),
        SOPStep(2, "Second step"),
        SOPStep(3, "Third step")
    ]
    
    metadata = SOPMetadata("1.0", "2024-01-01", "2024-01-01", "Author")
    
    sop = SOP(
        id="TEST-002",
        title="Test SOP",
        description="Test",
        category="clinical",
        priority="medium",
        steps=steps,
        metadata=metadata
    )
    
    step2 = sop.get_step(2)
    assert step2 is not None
    assert step2.step_number == 2
    assert step2.description == "Second step"
    
    step_invalid = sop.get_step(99)
    assert step_invalid is None
    
    print(f"  Retrieved step 2: {step2.description}")
    print(f"  Invalid step 99: {step_invalid}")
    print("✅ PASSED\n")


def test_sop_context():
    """Test SOP context"""
    print("Test: SOPContext")
    
    context = SOPContext(
        department="cardiology",
        role="physician",
        task_type="admission",
        keywords=["cardiac", "patient"],
        priority="high",
        category="clinical"
    )
    
    assert context.department == "cardiology"
    assert len(context.keywords) == 2
    
    print(f"  Department: {context.department}")
    print(f"  Role: {context.role}")
    print(f"  Category: {context.category}")
    print(f"  Keywords: {context.keywords}")
    print("✅ PASSED\n")


def test_sop_context_matching():
    """Test context matching with SOPs"""
    print("Test: Context Matching")
    
    context = SOPContext(
        department="cardiology",
        category="clinical",
        keywords=["cardiac", "admission"]
    )
    
    # Matching SOP
    matching_sop = SOP(
        id="MATCH-001",
        title="Cardiac Admission",
        description="Test",
        category="clinical",
        priority="high",
        steps=[],
        metadata=SOPMetadata("1.0", "2024-01-01", "2024-01-01", "Author"),
        applicable_departments=["cardiology"],
        keywords=["cardiac", "admission"]
    )
    
    # Non-matching SOP
    non_matching_sop = SOP(
        id="NOMATCH-001",
        title="Admin Task",
        description="Test",
        category="administrative",
        priority="low",
        steps=[],
        metadata=SOPMetadata("1.0", "2024-01-01", "2024-01-01", "Author"),
        applicable_departments=["admin"],
        keywords=["filing"]
    )
    
    matches_1 = context.matches(matching_sop)
    matches_2 = context.matches(non_matching_sop)
    
    assert matches_1 is True, "Should match cardiac admission SOP"
    assert matches_2 is False, "Should not match admin SOP"
    
    print(f"  Context matches cardiac SOP: {matches_1}")
    print(f"  Context matches admin SOP: {matches_2}")
    print("✅ PASSED\n")


def test_sop_repository():
    """Test SOP repository"""
    print("Test: SOPRepository")
    
    repo = SOPRepository(
        name="test_repo",
        description="Test repository",
        source_type="local",
        source_url="/test/path"
    )
    
    # Add SOPs
    sop1 = SOP(
        id="TEST-001",
        title="Test SOP 1",
        description="First SOP",
        category="clinical",
        priority="high",
        steps=[],
        metadata=SOPMetadata("1.0", "2024-01-01", "2024-01-01", "Author"),
        keywords=["test"]
    )
    
    sop2 = SOP(
        id="TEST-002",
        title="Test SOP 2",
        description="Second SOP",
        category="safety",
        priority="critical",
        steps=[],
        metadata=SOPMetadata("1.0", "2024-01-01", "2024-01-01", "Author"),
        keywords=["emergency"]
    )
    
    repo.add_sop(sop1)
    repo.add_sop(sop2)
    
    assert len(repo.sops) == 2
    
    # Test retrieval by ID
    retrieved = repo.get_sop_by_id("TEST-001")
    assert retrieved is not None
    assert retrieved.id == "TEST-001"
    
    # Test find by category
    clinical_sops = repo.find_sops_by_category("clinical")
    assert len(clinical_sops) == 1
    
    # Test find by keyword
    test_sops = repo.find_sops_by_keyword("test")
    assert len(test_sops) == 1
    
    # Test get categories
    categories = repo.get_all_categories()
    assert len(categories) == 2
    assert "clinical" in categories
    assert "safety" in categories
    
    print(f"  Repository: {repo.name}")
    print(f"  SOPs: {len(repo.sops)}")
    print(f"  Categories: {categories}")
    print("✅ PASSED\n")


def run_all_tests():
    """Run all model tests"""
    print("=" * 60)
    print("SOP DATA MODEL TESTS")
    print("=" * 60)
    print()
    
    test_sop_step_creation()
    test_sop_metadata()
    test_sop_creation()
    test_sop_get_step()
    test_sop_context()
    test_sop_context_matching()
    test_sop_repository()
    
    print("=" * 60)
    print("✅ ALL MODEL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
