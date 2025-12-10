"""
Context analysis for determining relevant SOPs
"""

import re
from typing import List, Dict, Optional
from .sop_models import SOPContext


class ContextAnalyzer:
    """Analyzes user queries to extract context for SOP loading"""
    
    # Keyword mappings for context detection
    CATEGORY_KEYWORDS = {
        'clinical': ['patient', 'diagnosis', 'treatment', 'procedure', 'examination', 'therapy', 
                    'clinical', 'medical', 'surgery', 'consultation', 'assessment'],
        'administrative': ['schedule', 'appointment', 'registration', 'billing', 'insurance',
                          'documentation', 'records', 'administrative', 'paperwork', 'form'],
        'safety': ['emergency', 'code', 'alert', 'hazard', 'incident', 'safety', 'protection',
                  'risk', 'accident', 'harm', 'danger'],
        'quality': ['quality', 'audit', 'review', 'compliance', 'standard', 'improvement',
                   'metric', 'performance', 'evaluation'],
        'compliance': ['compliance', 'regulation', 'policy', 'legal', 'hipaa', 'gdpr',
                      'requirement', 'mandate', 'law', 'rule'],
        'technical': ['equipment', 'system', 'device', 'technical', 'maintenance', 'calibration',
                     'setup', 'configuration', 'installation', 'repair'],
        'operational': ['workflow', 'process', 'operation', 'handoff', 'transfer', 'operational',
                       'logistics', 'transport', 'inventory']
    }
    
    DEPARTMENT_KEYWORDS = {
        'cardiology': ['cardiac', 'heart', 'cardiology', 'cardiovascular', 'ecg', 'ekg'],
        'oncology': ['cancer', 'oncology', 'tumor', 'chemotherapy', 'radiation', 'malignancy'],
        'emergency': ['emergency', 'er', 'trauma', 'urgent', 'critical', 'acute'],
        'pediatrics': ['pediatric', 'child', 'infant', 'neonatal', 'baby', 'adolescent'],
        'radiology': ['radiology', 'imaging', 'xray', 'ct', 'mri', 'ultrasound', 'scan'],
        'pharmacy': ['pharmacy', 'medication', 'drug', 'prescription', 'pharmaceutical'],
        'laboratory': ['lab', 'laboratory', 'specimen', 'test', 'sample', 'analysis'],
        'surgery': ['surgery', 'surgical', 'operation', 'operative', 'perioperative'],
        'icu': ['icu', 'intensive', 'critical care', 'ventilator', 'monitoring']
    }
    
    ROLE_KEYWORDS = {
        'physician': ['doctor', 'physician', 'md', 'attending', 'consultant'],
        'nurse': ['nurse', 'rn', 'lpn', 'nursing'],
        'technician': ['technician', 'tech', 'technologist'],
        'pharmacist': ['pharmacist', 'pharmacy'],
        'administrator': ['administrator', 'manager', 'director', 'coordinator'],
        'therapist': ['therapist', 'therapy']
    }
    
    TASK_KEYWORDS = {
        'admission': ['admit', 'admission', 'intake'],
        'discharge': ['discharge', 'release', 'dismissal'],
        'transfer': ['transfer', 'handoff', 'transition'],
        'consultation': ['consult', 'consultation', 'referral'],
        'procedure': ['procedure', 'intervention', 'operation'],
        'administration': ['administer', 'administration', 'give', 'deliver'],
        'documentation': ['document', 'documentation', 'record', 'chart'],
        'assessment': ['assess', 'assessment', 'evaluate', 'examination']
    }
    
    PRIORITY_KEYWORDS = {
        'critical': ['emergency', 'critical', 'urgent', 'code', 'immediate', 'stat'],
        'high': ['important', 'priority', 'significant', 'serious'],
        'medium': ['routine', 'standard', 'normal'],
        'low': ['minor', 'low', 'non-urgent', 'elective']
    }
    
    def analyze(self, query: str, conversation_history: Optional[List[str]] = None) -> SOPContext:
        """
        Analyze a query to extract context for SOP matching
        
        Args:
            query: User query text
            conversation_history: Previous messages for additional context
            
        Returns:
            SOPContext with extracted information
            
        Raises:
            ValueError: If query is empty or None
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        query_lower = query.lower()
        
        # Extract keywords from query
        keywords = self._extract_keywords(query_lower)
        
        # Detect category
        category = self._detect_category(query_lower, keywords)
        
        # Detect department
        department = self._detect_department(query_lower, keywords)
        
        # Detect role
        role = self._detect_role(query_lower, keywords, conversation_history)
        
        # Detect task type
        task_type = self._detect_task_type(query_lower, keywords)
        
        # Detect priority
        priority = self._detect_priority(query_lower, keywords)
        
        return SOPContext(
            department=department,
            role=role,
            task_type=task_type,
            keywords=keywords,
            priority=priority,
            category=category
        )
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query"""
        # Remove common stop words
        stop_words = {'i', 'me', 'my', 'we', 'to', 'the', 'a', 'an', 'and', 'or', 'but',
                     'in', 'on', 'at', 'for', 'with', 'from', 'of', 'is', 'are', 'was',
                     'need', 'want', 'can', 'how', 'what', 'when', 'where', 'who', 'do'}
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords[:10]  # Limit to top 10 keywords
    
    def _detect_category(self, query: str, keywords: List[str]) -> Optional[str]:
        """Detect SOP category from query"""
        scores = {}
        
        for category, category_keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in category_keywords if kw in query)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        return None
    
    def _detect_department(self, query: str, keywords: List[str]) -> Optional[str]:
        """Detect department from query"""
        for department, dept_keywords in self.DEPARTMENT_KEYWORDS.items():
            if any(kw in query for kw in dept_keywords):
                return department
        return None
    
    def _detect_role(self, query: str, keywords: List[str], 
                     conversation_history: Optional[List[str]] = None) -> Optional[str]:
        """Detect user role from query or conversation history"""
        # Check current query
        for role, role_keywords in self.ROLE_KEYWORDS.items():
            if any(kw in query for kw in role_keywords):
                return role
        
        # Check conversation history if available
        if conversation_history:
            for message in conversation_history[-5:]:  # Check last 5 messages
                message_lower = message.lower()
                for role, role_keywords in self.ROLE_KEYWORDS.items():
                    if any(kw in message_lower for kw in role_keywords):
                        return role
        
        return None
    
    def _detect_task_type(self, query: str, keywords: List[str]) -> Optional[str]:
        """Detect task type from query"""
        for task, task_keywords in self.TASK_KEYWORDS.items():
            if any(kw in query for kw in task_keywords):
                return task
        return None
    
    def _detect_priority(self, query: str, keywords: List[str]) -> Optional[str]:
        """Detect priority level from query"""
        for priority, priority_keywords in self.PRIORITY_KEYWORDS.items():
            if any(kw in query for kw in priority_keywords):
                return priority
        return 'medium'  # Default to medium if no priority indicators found
    
    def get_context_summary(self, context: SOPContext) -> str:
        """Generate a human-readable summary of the context"""
        parts = []
        
        if context.category:
            parts.append(f"Category: {context.category}")
        if context.department:
            parts.append(f"Department: {context.department}")
        if context.role:
            parts.append(f"Role: {context.role}")
        if context.task_type:
            parts.append(f"Task: {context.task_type}")
        if context.priority:
            parts.append(f"Priority: {context.priority}")
        if context.keywords:
            parts.append(f"Keywords: {', '.join(context.keywords[:5])}")
        
        return "\n".join(f"  • {part}" for part in parts) if parts else "  • No specific context detected"
