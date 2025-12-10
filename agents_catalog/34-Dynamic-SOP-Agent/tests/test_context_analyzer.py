"""
Tests for Context Analyzer
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.context_analyzer import ContextAnalyzer
from src.models.sop_models import SOP, SOPStep, SOPMetadata


def test_analyze_query_clinical():
    """Test context analysis for clinical query"""
    analyzer = ContextAnalyzer()
    
    query = "I need to admit a cardiac patient to the ICU"
    context = analyzer.analyze_query(query)
    
    print("Test: Clinical Query Analysis")
    print(f"Query: {query}")
    print(f"Category: {context.category}")
    print(f"Department: {context.department}")
    print(f"Keywords: {context.keywords}")
    print(f"Priority: {context.priority}")
    
    assert context.category == 'clinical', "Should detect clinical category"
    assert context.department == 'cardiology', "Should detect cardiology department"
    assert 'patient' in context.keywords, "Should extract 'patient' keyword"
    print("✅ PASSED\n")


def test_analyze_query_emergency():
    """Test context analysis for emergency query"""
    analyzer = ContextAnalyzer()
    
    query = "Emergency code blue in room 301"
    context = analyzer.analyze_query(query)
    
    print("Test: Emergency Query Analysis")
    print(f"Query: {query}")
    print(f"Category: {context.category}")
    print(f"Department: {context.department}")
    print(f"Priority: {context.priority}")
    
    assert context.category == 'safety', "Should detect safety category"
    assert context.department == 'emergency', "Should detect emergency department"
    assert context.priority == 'critical', "Should detect critical priority"
    print("✅ PASSED\n")


def test_analyze_query_medication():
    """Test context analysis for medication query"""
    analyzer = ContextAnalyzer()
    
    query = "How do I safely administer IV medication to a patient"
    context = analyzer.analyze_query(query)
    
    print("Test: Medication Query Analysis")
    print(f"Query: {query}")
    print(f"Category: {context.category}")
    print(f"Department: {context.department}")
    print(f"Role: {context.role}")
    print(f"Keywords: {context.keywords}")
    
    assert 'medication' in context.keywords or 'patient' in context.keywords
    print("✅ PASSED\n")


def test_determine_category():
    """Test category determination"""
    analyzer = ContextAnalyzer()
    
    test_cases = [
        ("patient treatment procedure", "clinical"),
        ("schedule appointment", "administrative"),
        ("emergency evacuation", "safety"),
        ("quality audit checklist", "quality"),
    ]
    
    print("Test: Category Determination")
    for query, expected_category in test_cases:
        category = analyzer._determine_category(query, [])
        print(f"Query: '{query}' -> Category: {category}")
        assert category == expected_category, f"Expected {expected_category}, got {category}"
    
    print("✅ PASSED\n")


def test_rank_sops_by_relevance():
    """Test SOP ranking by relevance"""
    analyzer = ContextAnalyzer()
    
    # Create test context
    from src.models.sop_models import SOPContext
    context = SOPContext(
        category="clinical",
        department="cardiology",
        keywords=["patient", "cardiac", "admission"]
    )
    
    # Create test SOPs
    sop1 = SOP(
        id="SOP-001",
        title="Cardiac Patient Admission",
        description="Admission procedure for cardiac patients",
        category="clinical",
        priority="high",
        steps=[],
        metadata=SOPMetadata("1.0", "2024-01-01", "2024-01-01", "Test"),
        applicable_departments=["cardiology"],
        keywords=["cardiac", "admission", "patient"]
    )
    
    sop2 = SOP(
        id="SOP-002",
        title="General Admin Task",
        description="Administrative task",
        category="administrative",
        priority="low",
        steps=[],
        metadata=SOPMetadata("1.0", "2024-01-01", "2024-01-01", "Test"),
        applicable_departments=["admin"],
        keywords=["filing", "paperwork"]
    )
    
    sops = [sop1, sop2]
    ranked = analyzer.rank_sops_by_relevance(context, sops)
    
    print("Test: SOP Ranking by Relevance")
    for sop, score in ranked:
        print(f"SOP: {sop.id} - Score: {score}")
    
    assert ranked[0][0].id == "SOP-001", "Cardiac SOP should rank first"
    assert ranked[0][1] > ranked[1][1], "Cardiac SOP should have higher score"
    print("✅ PASSED\n")


def run_all_tests():
    """Run all context analyzer tests"""
    print("=" * 60)
    print("CONTEXT ANALYZER TESTS")
    print("=" * 60)
    print()
    
    test_analyze_query_clinical()
    test_analyze_query_emergency()
    test_analyze_query_medication()
    test_determine_category()
    test_rank_sops_by_relevance()
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
