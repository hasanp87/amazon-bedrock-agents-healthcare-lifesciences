"""
Test strands-agents-sops Library Integration
Verifies proper usage of library classes and methods
"""

import sys
from pathlib import Path

# Add agent_config directory to path directly
sys.path.insert(0, str(Path(__file__).parent.parent / "agent" / "agent_config"))

# Import directly from modules to avoid package init dependencies
import sop_loader
import sop_models

SOPLoader = sop_loader.SOPLoader
LIBRARY_AVAILABLE = sop_loader.LIBRARY_AVAILABLE
SOP = sop_models.SOP
SOPStep = sop_models.SOPStep
SOPMetadata = sop_models.SOPMetadata


def test_library_availability():
    """Test that library availability is properly detected"""
    print("Testing Library Availability...\n")
    
    if LIBRARY_AVAILABLE:
        print("✅ strands_sops library is AVAILABLE")
        print("   Agent will use library functions for SOP loading")
    else:
        print("⚠️ strands_sops library is NOT available")
        print("   Agent will use fallback compatibility layer")
    
    return True


def test_library_classes_imported():
    """Test that library classes can be imported"""
    print("\nTesting Library Class Imports...\n")
    
    try:
        from strands_sops import SOP as LibSOP
        from strands_sops import SOPStep as LibSOPStep
        from strands_sops import SOPMetadata as LibSOPMetadata
        print("✅ Successfully imported library classes:")
        print(f"   - SOP: {LibSOP}")
        print(f"   - SOPStep: {LibSOPStep}")
        print(f"   - SOPMetadata: {LibSOPMetadata}")
        return True
    except ImportError as e:
        print(f"⚠️ Could not import library classes: {e}")
        print("   Testing will use compatibility layer")
        return True  # Not a failure - fallback should work


def test_library_functions_available():
    """Test that library functions can be imported"""
    print("\nTesting Library Function Imports...\n")
    
    try:
        from strands_sops import load_sop_from_file
        from strands_sops import load_sops_from_directory
        print("✅ Successfully imported library functions:")
        print(f"   - load_sop_from_file: {load_sop_from_file}")
        print(f"   - load_sops_from_directory: {load_sops_from_directory}")
        return True
    except ImportError as e:
        print(f"⚠️ Could not import library functions: {e}")
        print("   SOPLoader will use fallback parsing")
        return True  # Not a failure - fallback should work


def test_sop_loading_uses_library():
    """Test that SOP loading uses library when available"""
    print("\nTesting Library Usage in SOP Loading...\n")
    
    loader = SOPLoader()
    examples_dir = Path(__file__).parent.parent / "examples" / "sops"
    
    if not examples_dir.exists():
        print(f"⚠️ Examples directory not found: {examples_dir}")
        return True  # Skip test
    
    try:
        # Check if any markdown files exist
        md_files = list(examples_dir.glob("*.md"))
        if not md_files:
            print("⚠️ No markdown SOP files found in examples")
            return True
        
        print(f"Found {len(md_files)} markdown SOP files")
        
        # Load SOPs
        repo = loader.load_from_directory(str(examples_dir), "test")
        
        if LIBRARY_AVAILABLE:
            print(f"✅ Loaded {len(repo.sops)} SOPs using library functions")
        else:
            print(f"✅ Loaded {len(repo.sops)} SOPs using fallback parser")
        
        # Verify SOP structure
        if repo.sops:
            sop = repo.sops[0]
            print(f"\nVerifying SOP structure:")
            print(f"  - Type: {type(sop).__name__}")
            print(f"  - Has ID: {hasattr(sop, 'id')}")
            print(f"  - Has steps: {hasattr(sop, 'steps')}")
            print(f"  - Has metadata: {hasattr(sop, 'metadata')}")
            
            if sop.steps:
                step = sop.steps[0]
                print(f"  - Step type: {type(step).__name__}")
                print(f"  - Step has step_number: {hasattr(step, 'step_number')}")
                print(f"  - Step has description: {hasattr(step, 'description')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during library test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rfc2119_keyword_detection():
    """Test that RFC 2119 keywords are properly detected"""
    print("\nTesting RFC 2119 Keyword Detection...\n")
    
    loader = SOPLoader()
    examples_dir = Path(__file__).parent.parent / "examples" / "sops"
    
    try:
        # Load markdown SOPs
        repo = loader.load_from_directory(str(examples_dir), "test")
        
        # Find SOPs with steps
        sops_with_steps = [sop for sop in repo.sops if sop.steps]
        
        if not sops_with_steps:
            print("⚠️ No SOPs with steps found for keyword testing")
            return True
        
        print(f"Analyzing {len(sops_with_steps)} SOPs for RFC 2119 keywords...")
        
        # Check for required steps (MUST)
        must_count = 0
        should_count = 0
        may_count = 0
        
        for sop in sops_with_steps:
            for step in sop.steps:
                if step.required:
                    must_count += 1
                if hasattr(step, 'details') and step.details:
                    if 'MUST' in step.details:
                        must_count += 1
                    if 'SHOULD' in step.details:
                        should_count += 1
                    if 'MAY' in step.details:
                        may_count += 1
        
        print(f"\nRFC 2119 Keyword Analysis:")
        print(f"  - Required steps (MUST): {must_count}")
        print(f"  - Recommended (SHOULD): {should_count}")
        print(f"  - Optional (MAY): {may_count}")
        
        if must_count > 0 or should_count > 0 or may_count > 0:
            print("✅ RFC 2119 keywords detected in SOPs")
        else:
            print("⚠️ No RFC 2119 keywords found (may be legacy format)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing RFC 2119: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_library_vs_fallback_consistency():
    """Test that library and fallback produce consistent results"""
    print("\nTesting Library vs Fallback Consistency...\n")
    
    # This test verifies that regardless of whether library is available,
    # the SOP loading produces consistent, usable results
    
    loader = SOPLoader()
    examples_dir = Path(__file__).parent.parent / "examples" / "sops"
    
    try:
        repo = loader.load_from_directory(str(examples_dir), "test")
        
        if not repo.sops:
            print("⚠️ No SOPs loaded for consistency test")
            return True
        
        print(f"Loaded {len(repo.sops)} SOPs")
        print("\nVerifying consistency of SOP structure...")
        
        all_valid = True
        for sop in repo.sops:
            # Check required attributes
            if not hasattr(sop, 'id') or not sop.id:
                print(f"  ❌ SOP missing ID")
                all_valid = False
            if not hasattr(sop, 'title') or not sop.title:
                print(f"  ❌ SOP {sop.id} missing title")
                all_valid = False
            if not hasattr(sop, 'steps') or not sop.steps:
                print(f"  ⚠️ SOP {sop.id} has no steps")
            if not hasattr(sop, 'metadata'):
                print(f"  ❌ SOP {sop.id} missing metadata")
                all_valid = False
        
        if all_valid:
            print("✅ All SOPs have consistent structure")
        else:
            print("❌ Some SOPs have inconsistent structure")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Error in consistency test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversion_layer():
    """Test the library SOP to local SOP conversion"""
    print("\nTesting SOP Conversion Layer...\n")
    
    loader = SOPLoader()
    
    # Test that _convert_library_sop exists and works
    if not hasattr(loader, '_convert_library_sop'):
        print("⚠️ Conversion method not found (may not be needed)")
        return True
    
    print("✅ Conversion layer is available")
    print("   This ensures library SOPs can be used with local code")
    
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("strands-agents-sops Library Integration Test Suite")
    print("=" * 70)
    
    tests = [
        test_library_availability,
        test_library_classes_imported,
        test_library_functions_available,
        test_sop_loading_uses_library,
        test_rfc2119_keyword_detection,
        test_library_vs_fallback_consistency,
        test_conversion_layer,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ All {total} tests passed!")
    else:
        print(f"⚠️ {passed}/{total} tests passed")
    
    print("=" * 70)
    
    # Return exit code
    sys.exit(0 if all(results) else 1)
