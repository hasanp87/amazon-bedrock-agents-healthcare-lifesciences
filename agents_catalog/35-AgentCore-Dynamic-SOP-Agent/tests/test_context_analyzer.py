"""
Test Context Analyzer functionality
"""

import sys
from pathlib import Path

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

from agent_config.context_analyzer import ContextAnalyzer
from agent_config.sop_loader import SOPLoader


def test_context_extraction():
    """Test extracting context from various queries"""
    print("Testing Context Extraction...\n")
    
    analyzer = ContextAnalyzer()
    
    test_queries = [
        "I need to admit a cardiac patient to the ICU",
        "Emergency code blue in room 301",
        "How do I safely administer IV medications",
        "Need to schedule a follow-up cardiology appointment",
        "Patient discharge procedure for pediatric ward"
    ]
    
    print("📝 Test Queries and Extracted Context:\n")
    
    for query in test_queries:
        print(f"Query: '{query}'")
        context = analyzer.analyze(query)
        
        print(f"  Category: {context.category}")
        print(f"  Department: {context.department}")
        print(f"  Role: {context.role}")
        print(f"  Task Type: {context.task_type}")
        print(f"  Priority: {context.priority}")
        print(f"  Keywords: {', '.join(context.keywords[:5])}")
        print()
    
    return True


def test_sop_matching():
    """Test matching SOPs based on context"""
    print("\nTesting SOP Matching with Context...\n")
    
    analyzer = ContextAnalyzer()
    loader = SOPLoader()
    
    examples_dir = Path(__file__).parent.parent / "examples" / "sops"
    
    if not examples_dir.exists():
        print(f"❌ Examples directory not found")
        return False
    
    try:
        repo = loader.load_from_directory(str(examples_dir), "test_repo")
        
        test_queries = [
            "I need to admit a cardiac patient to intensive care",
            "Emergency cardiac arrest situation",
            "Need to give medication to patient"
        ]
        
        for query in test_queries:
            print(f"🔍 Query: '{query}'")
            context = analyzer.analyze(query)
            
            # Get matching SOPs with scores
            matches = repo.find_sops_by_context(context)
            
            if matches:
                print(f"   Found {len(matches)} matching SOPs:")
                for sop, score in matches[:3]:  # Show top 3
                    print(f"   • {sop.id}: {sop.title} (score: {score:.1f})")
            else:
                print(f"   No matching SOPs found")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_summary():
    """Test context summary generation"""
    print("\nTesting Context Summary Generation...\n")
    
    analyzer = ContextAnalyzer()
    
    query = "Emergency code blue in cardiac ICU room 301"
    context = analyzer.analyze(query)
    summary = analyzer.get_context_summary(context)
    
    print(f"Query: '{query}'")
    print(f"\nContext Summary:")
    print(summary)
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Context Analyzer Test Suite")
    print("=" * 60)
    print()
    
    success = True
    success = test_context_extraction() and success
    success = test_sop_matching() and success
    success = test_context_summary() and success
    
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
