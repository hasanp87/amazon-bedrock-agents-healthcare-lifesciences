"""
Data models for Standard Operating Procedures (SOPs)
Integrated with AgentCore and Strands framework
Uses strands-agents-sops library classes
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

# Import from strands-agents-sops library
try:
    from strands_sops import SOP as LibrarySOP
    from strands_sops import SOPStep as LibrarySOPStep
    from strands_sops import SOPMetadata as LibrarySOPMetadata
    LIBRARY_AVAILABLE = True
except ImportError:
    # Fallback for development/testing without library installed
    LIBRARY_AVAILABLE = False
    print("⚠️ Warning: strands_sops library not available, using compatibility layer")


class SOPCategory(str, Enum):
    """Categories for SOPs"""
    CLINICAL = "clinical"
    ADMINISTRATIVE = "administrative"
    SAFETY = "safety"
    QUALITY = "quality"
    COMPLIANCE = "compliance"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"


class SOPPriority(str, Enum):
    """Priority levels for SOPs"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# If library is available, use library classes directly; otherwise provide compatibility layer
if LIBRARY_AVAILABLE:
    # Use library classes as base
    SOPStep = LibrarySOPStep
    SOPMetadata = LibrarySOPMetadata
    
    # Extend library SOP class if needed for backward compatibility
    class SOP(LibrarySOP):
        """Extended SOP class based on strands_sops.SOP"""
        pass
else:
    # Compatibility layer when library is not available
    @dataclass
    class SOPStep:
        """Individual step within an SOP - compatibility layer"""
        step_number: int
        description: str
        details: Optional[str] = None
        required: bool = True
        validation_criteria: Optional[List[str]] = None
        estimated_time: Optional[str] = None
        warnings: Optional[List[str]] = None
        
        def to_dict(self) -> Dict[str, Any]:
            return asdict(self)


    @dataclass
    class SOPMetadata:
        """Metadata for an SOP - compatibility layer"""
        version: str
        created_date: str
        last_updated: str
        author: str
        reviewer: Optional[str] = None
        approval_status: str = "draft"
        review_frequency: Optional[str] = None
        
        def to_dict(self) -> Dict[str, Any]:
            return asdict(self)


    @dataclass
    class SOP:
        """Standard Operating Procedure - compatibility layer"""
        id: str
        title: str
        description: str
        category: str
        priority: str
        steps: List['SOPStep']
        metadata: 'SOPMetadata'
        applicable_departments: List[str] = field(default_factory=list)
        applicable_roles: List[str] = field(default_factory=list)
        keywords: List[str] = field(default_factory=list)
        prerequisites: Optional[List[str]] = None
        related_sops: Optional[List[str]] = None
        references: Optional[List[str]] = None
        
        def to_dict(self) -> Dict[str, Any]:
            data = asdict(self)
            data['steps'] = [step.to_dict() if hasattr(step, 'to_dict') else asdict(step) for step in self.steps]
            data['metadata'] = self.metadata.to_dict() if hasattr(self.metadata, 'to_dict') else asdict(self.metadata)
            return data
        
        def get_step(self, step_number: int) -> Optional['SOPStep']:
            """Retrieve a specific step by number"""
            for step in self.steps:
                if step.step_number == step_number:
                    return step
            return None
        
        def get_summary(self) -> str:
            """Get a brief summary of the SOP"""
            return f"SOP {self.id}: {self.title} ({len(self.steps)} steps, {self.priority} priority)"


@dataclass
class SOPContext:
    """Context information for determining which SOPs to load"""
    department: Optional[str] = None
    role: Optional[str] = None
    task_type: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    priority: Optional[str] = None
    category: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def calculate_relevance_score(self, sop: 'SOP') -> float:
        """Calculate relevance score for an SOP based on this context"""
        score = 0.0
        
        # Category match (highest priority)
        if self.category and self.category.lower() == sop.category.lower():
            score += 10.0
        
        # Department match
        if self.department and self.department.lower() in [d.lower() for d in sop.applicable_departments]:
            score += 8.0
        
        # Role match
        if self.role and self.role.lower() in [r.lower() for r in sop.applicable_roles]:
            score += 5.0
        
        # Priority match
        if self.priority and self.priority.lower() == sop.priority.lower():
            score += 2.0
        
        # Keyword matches
        sop_keywords = [k.lower() for k in sop.keywords]
        context_keywords = [k.lower() for k in self.keywords]
        keyword_matches = len(set(sop_keywords) & set(context_keywords))
        score += keyword_matches * 2.0
        
        return score


@dataclass
class SOPRepository:
    """Repository for managing multiple SOPs"""
    name: str
    description: str
    source_type: str  # "local", "mcp", "git", "api"
    source_url: Optional[str] = None
    sops: List[SOP] = field(default_factory=list)
    last_sync: Optional[str] = None
    
    def add_sop(self, sop: SOP) -> None:
        """Add an SOP to the repository"""
        self.sops.append(sop)
    
    def get_sop_by_id(self, sop_id: str) -> Optional[SOP]:
        """Retrieve an SOP by ID"""
        for sop in self.sops:
            if sop.id == sop_id:
                return sop
        return None
    
    def find_sops_by_context(self, context: SOPContext) -> List[tuple[SOP, float]]:
        """Find SOPs that match the given context with relevance scores"""
        scored_sops = []
        for sop in self.sops:
            score = context.calculate_relevance_score(sop)
            if score > 0:
                scored_sops.append((sop, score))
        
        # Sort by score descending
        scored_sops.sort(key=lambda x: x[1], reverse=True)
        return scored_sops
    
    def find_sops_by_category(self, category: str) -> List[SOP]:
        """Find all SOPs in a specific category"""
        return [sop for sop in self.sops if sop.category.lower() == category.lower()]
    
    def find_sops_by_keyword(self, keyword: str) -> List[SOP]:
        """Find SOPs containing a specific keyword"""
        keyword_lower = keyword.lower()
        return [sop for sop in self.sops 
                if keyword_lower in [k.lower() for k in sop.keywords]]
    
    def get_all_categories(self) -> List[str]:
        """Get list of all unique categories in the repository"""
        return list(set(sop.category for sop in self.sops))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'source_type': self.source_type,
            'source_url': self.source_url,
            'last_sync': self.last_sync,
            'sop_count': len(self.sops),
            'categories': self.get_all_categories()
        }


@dataclass
class SOPExecution:
    """Track execution of an SOP"""
    sop_id: str
    started_at: str
    current_step: int = 1
    completed_steps: List[int] = field(default_factory=list)
    skipped_steps: List[tuple[int, str]] = field(default_factory=list)  # (step_number, reason)
    step_notes: Dict[int, str] = field(default_factory=dict)
    completed: bool = False
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
