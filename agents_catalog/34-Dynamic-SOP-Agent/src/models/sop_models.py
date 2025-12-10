"""
Data models for Standard Operating Procedures (SOPs)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


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


@dataclass
class SOPStep:
    """Individual step within an SOP"""
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
    """Metadata for an SOP"""
    version: str
    created_date: str
    last_updated: str
    author: str
    reviewer: Optional[str] = None
    approval_status: str = "draft"
    review_frequency: Optional[str] = None  # e.g., "annual", "quarterly"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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
    
    def matches(self, sop: 'SOP') -> bool:
        """Check if this context matches an SOP's applicability"""
        score = 0
        
        # Check department match
        if self.department and self.department.lower() in [d.lower() for d in sop.applicable_departments]:
            score += 3
        
        # Check role match
        if self.role and self.role.lower() in [r.lower() for r in sop.applicable_roles]:
            score += 3
        
        # Check category match
        if self.category and self.category.lower() == sop.category.lower():
            score += 2
        
        # Check keyword matches
        sop_keywords = [k.lower() for k in sop.keywords]
        context_keywords = [k.lower() for k in self.keywords]
        keyword_matches = len(set(sop_keywords) & set(context_keywords))
        score += keyword_matches
        
        return score > 0


@dataclass
class SOP:
    """Standard Operating Procedure"""
    id: str
    title: str
    description: str
    category: str
    priority: str
    steps: List[SOPStep]
    metadata: SOPMetadata
    applicable_departments: List[str] = field(default_factory=list)
    applicable_roles: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    prerequisites: Optional[List[str]] = None
    related_sops: Optional[List[str]] = None
    references: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['steps'] = [step.to_dict() for step in self.steps]
        data['metadata'] = self.metadata.to_dict()
        return data
    
    def get_step(self, step_number: int) -> Optional[SOPStep]:
        """Retrieve a specific step by number"""
        for step in self.steps:
            if step.step_number == step_number:
                return step
        return None
    
    def get_summary(self) -> str:
        """Get a brief summary of the SOP"""
        return f"SOP {self.id}: {self.title} ({len(self.steps)} steps, {self.priority} priority)"


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
    
    def find_sops_by_context(self, context: SOPContext) -> List[SOP]:
        """Find SOPs that match the given context"""
        matching_sops = []
        for sop in self.sops:
            if context.matches(sop):
                matching_sops.append(sop)
        return matching_sops
    
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
