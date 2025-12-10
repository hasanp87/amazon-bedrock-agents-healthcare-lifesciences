# Strands agent-sop Framework Integration

## Overview

This Dynamic SOP Agent now integrates with the **Strands agent-sop framework** - a standardized markdown format for defining AI agent workflows in natural language. This integration represents a significant improvement over generic SOP implementations by providing structured guidance with flexibility through RFC 2119 keyword-based constraints.

## What is Strands agent-sop?

The Strands agent-sop framework (from https://github.com/strands-agents/agent-sop) is an open-source specification that:

1. **Uses Markdown Format**: SOPs are written in human-readable markdown files
2. **Implements RFC 2119 Keywords**: Uses standardized keywords (MUST, SHOULD, MAY) to define constraint levels
3. **Provides Flexibility with Control**: Balances structured guidance with agent autonomy
4. **Enables Reusability**: SOPs become portable templates that work across different AI systems
5. **Improves Reliability**: Clear constraint levels reduce unpredictable agent behavior

## RFC 2119 Keywords Explained

The framework uses RFC 2119 standard keywords to define different levels of requirements:

### MUST / REQUIRED / SHALL
- **Meaning**: Absolute requirement
- **Usage**: Critical actions that cannot be skipped
- **Examples**: Safety checks, regulatory compliance, patient identification
- **Non-compliance**: May result in safety issues, regulatory violations, or system failures

### SHOULD / RECOMMENDED
- **Meaning**: Strong recommendation with room for justified deviation
- **Usage**: Best practices that should normally be followed
- **Examples**: Preferred procedures, quality improvements, efficiency measures
- **Deviation**: Acceptable with documented justification

### MAY / OPTIONAL
- **Meaning**: Truly optional action
- **Usage**: Additional helpful actions that can be taken at discretion
- **Examples**: Optional consultations, additional monitoring, convenience features
- **Discretion**: User can decide based on situation and judgment

### MUST NOT / SHALL NOT
- **Meaning**: Absolute prohibition
- **Usage**: Actions that are forbidden
- **Examples**: Contraindicated procedures, safety violations

## SOP Markdown Format

### File Structure

```markdown
# SOP Title

**SOP ID:** SOP-XXX-001  
**Category:** clinical|safety|operational|...  
**Priority:** critical|high|medium|low  
**Version:** 1.0  
**Last Updated:** YYYY-MM-DD  
**Applicable Departments:** Dept1, Dept2  
**Applicable Roles:** Role1, Role2

## Overview

Brief description of the SOP purpose and scope.

## Prerequisites

- Prerequisite item 1
- Prerequisite item 2

## Procedure

### Step 1: Step Title

**Description:** Brief description of what this step accomplishes

You MUST perform action X. You SHOULD consider factor Y. You MAY optionally do Z.

**Validation Criteria:**
- Criterion 1
- Criterion 2

**Warnings:**
- Warning 1
- Warning 2

**Estimated Time:** X minutes

---

### Step 2: Next Step

...

## Related SOPs

- Related SOP Title (SOP-XXX-002)

## References

- Reference 1
- Reference 2

## Approval

- **Author:** Name, Role
- **Reviewer:** Name, Role
- **Approval Status:** approved|draft
- **Review Frequency:** Annual
```

## Integration Architecture

### 1. SOP Loading Pipeline

```
Markdown File
    ↓
SOPLoader._load_sop_from_markdown()
    ↓
Parse metadata (SOP ID, category, priority, etc.)
    ↓
Parse steps with RFC 2119 keywords
    ↓
Extract validation criteria and warnings
    ↓
Create SOP object
    ↓
Add to repository
    ↓
Available to agent
```

### 2. Key Components Updated

#### SOPLoader (`sop_loader.py`)
- **Added**: `_load_sop_from_markdown()` method
- **Functionality**: Parses markdown files with regex patterns
- **Features**:
  - Extracts metadata from front matter
  - Parses step sections with RFC 2119 keywords
  - Extracts validation criteria, warnings, time estimates
  - Handles related SOPs and references
  - Generates keywords from content

#### DynamicSOPAgent (`agent.py`)
- **Updated**: System prompt to explain RFC 2119 semantics
- **Added**: Instructions for constraint level interpretation
- **Enhanced**: Context awareness for MUST vs SHOULD vs MAY actions

#### Example SOPs
- **Created**: `cardiac_icu_admission.md` - Clinical SOP with RFC 2119 keywords
- **Created**: `emergency_code_blue.md` - Critical safety SOP
- **Format**: Full markdown with proper RFC 2119 usage

### 3. Agent Behavior with agent-sop

The agent now understands and communicates constraint levels:

**User**: "Can I skip checking the patient's allergies?"

**Agent**: "No, checking allergies is a MUST requirement in the medication administration SOP. This is a critical safety check that cannot be skipped. It helps prevent potentially life-threatening allergic reactions."

**User**: "Should I involve a specialist?"

**Agent**: "The SOP says you SHOULD consult with a specialist for complex cases. This is a strong recommendation. You may proceed without consultation if you have sufficient expertise and document your reasoning, but it's generally recommended to get a second opinion."

**User**: "Can I use the electronic checklist?"

**Agent**: "Yes, you MAY use the electronic checklist - it's an optional tool that some clinicians find helpful. You can also use the paper checklist or your own documentation method. This is at your discretion."

## Benefits of agent-sop Integration

### 1. Standardization
- Portable SOP format that works across different systems
- Industry-standard RFC 2119 keywords familiar to technical users
- Consistent interpretation of requirements vs recommendations

### 2. Flexibility with Control
- Clear delineation between absolute requirements and best practices
- Agents can adapt SHOULD/MAY items to context while respecting MUST items
- Reduces overly rigid workflows while maintaining safety

### 3. Improved Communication
- Users understand what's mandatory vs recommended
- Clearer expectations for compliance
- Better justification for deviations from best practices

### 4. Maintainability
- Human-readable markdown format
- Easy to update and version control
- No complex JSON/YAML schemas
- Can be authored by subject matter experts without technical knowledge

### 5. Compliance and Auditing
- Clear audit trail of MUST requirements
- Documented justifications for SHOULD deviations
- Regulatory alignment through RFC 2119 standard

## Usage Examples

### Creating a New SOP

```markdown
# Patient Handoff Protocol

**SOP ID:** SOP-COMM-001  
**Category:** clinical  
**Priority:** high  

## Procedure

### Step 1: Prepare Handoff Information

**Description:** Gather all relevant patient information

You MUST include patient name, MRN, diagnosis, and current status. You SHOULD review recent lab results and medications. You MAY prepare a written handoff sheet if time permits.

**Validation Criteria:**
- All MUST items documented
- Critical information highlighted

**Estimated Time:** 5 minutes
```

### Agent Interpretation

The agent will:
1. **Enforce MUST requirements**: Verify patient identification data is complete
2. **Recommend SHOULD items**: Suggest reviewing labs but allow skipping if time-critical
3. **Offer MAY options**: Mention written handoff as a helpful option

### Search and Discovery

The agent can search for SOPs and understand their constraint patterns:

```python
# Agent searches for relevant SOPs
relevant_sops = search_sops_by_context("I need to perform a medication handoff")

# Returns SOPs with RFC 2119 constraint information
# Agent explains: "The Patient Handoff Protocol requires (MUST) certain
# critical information but allows flexibility (SHOULD/MAY) in documentation method."
```

## Migration from JSON/YAML to Markdown

The system now supports **both formats**:

### Legacy Format (Still Supported)
- JSON files (`*.json`)
- YAML files (`*.yaml`, `*.yml`)
- Custom data structure

### agent-sop Format (Recommended)
- Markdown files (`*.md`)
- RFC 2119 keywords
- Human-readable format

### Migration Strategy

1. **Keep existing JSON/YAML SOPs working** - No breaking changes
2. **Create new SOPs in markdown format** - Use agent-sop specification
3. **Gradually migrate critical SOPs** - Convert to markdown over time
4. **Retire old format eventually** - Once all SOPs migrated

## Best Practices

### When to Use MUST
- Safety-critical actions
- Regulatory requirements
- Legal compliance
- Actions that prevent harm
- Essential quality checks

### When to Use SHOULD
- Best practices
- Quality improvements
- Efficiency measures
- Standards of care
- Professional guidelines

### When to Use MAY
- Optional enhancements
- Convenience features
- Alternative methods
- Additional documentation
- Supplementary checks

### Writing Clear Steps

**Good Example:**
```markdown
You MUST verify patient identity with two identifiers before administering any medication.
You SHOULD check for drug interactions using the pharmacy system.
You MAY consult with a clinical pharmacist for complex regimens.
```

**Bad Example:**
```markdown
Verify the patient and check medications. Consider consulting pharmacy if needed.
```

The first example clearly delineates requirements vs recommendations. The second is ambiguous.

## Testing and Validation

### Unit Tests
```bash
python tests/test_sop_loader.py
```
Tests include:
- Markdown parsing
- RFC 2119 keyword extraction
- Metadata parsing
- Step structure validation

### Integration Tests
- Load markdown SOPs
- Verify agent understands constraint levels
- Test execution tracking
- Validate compliance checking

## Future Enhancements

### Planned Features
1. **Automated compliance checking** - Flag MUST violations
2. **Justification tracking** - Document SHOULD deviations
3. **SOP validation** - Check RFC 2119 usage consistency
4. **Template generation** - Create new SOPs from templates
5. **Multi-language support** - Translate RFC 2119 keywords
6. **Version comparison** - Diff SOPs with RFC 2119 tracking

### Integration Opportunities
1. **MCP Server for agent-sop** - Dedicated server for SOP management
2. **Git integration** - Version control for markdown SOPs
3. **SOP library** - Community-maintained SOP repository
4. **Compliance dashboards** - Visualize MUST vs SHOULD adherence

## Resources

### Official Documentation
- **Strands agent-sop GitHub**: https://github.com/strands-agents/agent-sop
- **AWS Blog Post**: https://aws.amazon.com/blogs/opensource/introducing-strands-agent-sops-natural-language-workflows-for-ai-agents/
- **RFC 2119 Specification**: https://www.ietf.org/rfc/rfc2119.txt

### Examples
- See `examples/sops/*.md` for markdown SOP examples
- See legacy `examples/sops/*.json` for comparison

### Tools
- **strands-agents-sops**: Python package for agent-sop support
- **SOPLoader**: Handles both markdown and legacy formats
- **Context Analyzer**: Understands RFC 2119 constraint levels

## Version History

- **v1.0** (2024-12-10): Initial integration with Strands agent-sop framework
  - Markdown SOP loading
  - RFC 2119 keyword parsing
  - Updated agent system prompt
  - Example markdown SOPs
  - Backward compatibility with JSON/YAML

## Support

For issues or questions about the agent-sop integration:
1. Review this documentation
2. Check example markdown SOPs in `examples/sops/`
3. Refer to Strands agent-sop repository
4. Review RFC 2119 specification for keyword semantics

---

**Last Updated:** December 10, 2024  
**Author:** Dynamic SOP Agent Team  
**Framework Version:** Strands agent-sop v1.0
