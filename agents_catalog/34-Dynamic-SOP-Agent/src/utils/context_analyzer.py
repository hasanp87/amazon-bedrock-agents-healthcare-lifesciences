"""
Context analysis utilities for determining which SOPs to load
"""

import re
from typing import List, Dict, Optional, Tuple
from ..models.sop_models import SOPContext, SOPCategory


class ContextAnalyzer:
    """Analyzes user queries and conversation context to determine relevant SOPs"""
    
    # Keywords mapped to categories
    CATEGORY_KEYWORDS = {
        'clinical': ['patient', 'treatment', 'diagnosis', 'medical', 'clinical', 'care', 
                     'therapy', 'procedure', 'examination', 'assessment'],
        'administrative': ['schedule', 'appointment', 'billing', 'insurance', 'documentation',
                          'record', 'filing', 'administrative', 'office', 'paperwork'],
        'safety': ['safety', 'emergency', 'hazard', 'incident', 'accident', 'risk',
                  'protective', 'evacuation', 'protocol', 'alert'],
        'quality': ['quality', 'improvement', 'audit', 'compliance', 'standard',
                   'accreditation', 'review', 'assessment', 'metrics'],
        'compliance': ['regulatory', 'compliance', 'hipaa', 'privacy', 'confidential',
                      'gdpr', 'regulation', 'legal', 'policy'],
        'technical': ['equipment', 'device', 'instrument', 'machine', 'technical',
                     'calibration', 'maintenance', 'troubleshoot', 'repair'],
        'operational': ['workflow', 'process', 'operation', 'procedure', 'routine',
                       'daily', 'shift', 'handoff', 'coordination']
    }
    
    # Department keywords
    DEPARTMENT_KEYWORDS = {
        'cardiology': ['heart', 'cardiac', 'cardiology', 'cardiovascular'],
        'oncology': ['cancer', 'oncology', 'tumor', 'chemotherapy', 'radiation'],
        'emergency': ['emergency', 'trauma', 'er', 'urgent', 'acute'],
        'pediatrics': ['pediatric', 'child', 'children', 'infant', 'neonatal'],
        'radiology': ['imaging', 'xray', 'x-ray', 'ct', 'mri', 'radiology'],
        'pharmacy': ['pharmacy', 'medication', 'drug', 'prescription', 'pharmacist'],
        'laboratory': ['lab', 'laboratory', 'test', 'specimen', 'sample'],
        'surgery': ['surgery', 'surgical', 'operation', 'operating room', 'or']
    }
    
    # Role keywords
    ROLE_KEYWORDS = {
        'physician': ['doctor', 'physician', 'md', 'attending'],
        'nurse': ['nurse', 'rn', 'lpn', 'nursing'],
        'technician': ['technician', 'tech', 'technologist'],
        'pharmacist': ['pharmacist', 'pharmacy'],
        'administrator': ['administrator', 'manager', 'supervisor', 'director'],
        'receptionist': ['receptionist', 'front desk', 'scheduling']
    }
    
    def __init__(self):
        """Initialize the context analyzer"""
        pass
    
    def analyze_query(self, query: str, conversation_history: Optional[List[str]] = None) -> SOPContext:
        """
        Analyze a user query to extract context information
        
        Args:
            query: User's query or message
            conversation_history: Previous messages in the conversation
            
        Returns:
            SOPContext object with extracted context information
        """
        query_lower = query.lower()
        
        # Extract keywords from the query
        keywords = self._extract_keywords(query_lower)
        
        # Determine category
        category = self._determine_category(query_lower, keywords)
        
        # Determine department
        department = self._determine_department(query_lower)
        
        # Determine role
        role = self._determine_role(query_lower)
        
        # Determine priority based on urgency indicators
        priority = self._determine_priority(query_lower)
        
        # If we have conversation history, incorporate it
        if conversation_history:
            historical_context = self._analyze_conversation_history(conversation_history)
            keywords.extend(historical_context.get('keywords', []))
            if not category and historical_context.get('category'):
                category = historical_context['category']
            if not department and historical_context.get('department'):
                department = historical_context['department']
        
        # Remove duplicates from keywords
        keywords = list(set(keywords))
        
        return SOPContext(
            department=department,
            role=role,
            task_type=self._extract_task_type(query_lower),
            keywords=keywords,
            priority=priority,
            category=category
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'can', 'what', 'how', 'when', 'where', 'why',
                     'who', 'which', 'this', 'that', 'these', 'those', 'i', 'you', 'we', 'they'}
        
        # Split text into words
        words = re.findall(r'\b[a-z]+\b', text)
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        return keywords[:10]  # Return top 10 keywords
    
    def _determine_category(self, text: str, keywords: List[str]) -> Optional[str]:
        """Determine the most likely category based on text and keywords"""
        category_scores = {cat: 0 for cat in self.CATEGORY_KEYWORDS.keys()}
        
        for category, cat_keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in cat_keywords:
                if keyword in text:
                    category_scores[category] += 1
        
        # Get category with highest score
        max_score = max(category_scores.values())
        if max_score > 0:
            for category, score in category_scores.items():
                if score == max_score:
                    return category
        
        return None
    
    def _determine_department(self, text: str) -> Optional[str]:
        """Determine the most likely department"""
        for department, dept_keywords in self.DEPARTMENT_KEYWORDS.items():
            for keyword in dept_keywords:
                if keyword in text:
                    return department
        return None
    
    def _determine_role(self, text: str) -> Optional[str]:
        """Determine the most likely role"""
        for role, role_keywords in self.ROLE_KEYWORDS.items():
            for keyword in role_keywords:
                if keyword in text:
                    return role
        return None
    
    def _determine_priority(self, text: str) -> str:
        """Determine priority level based on urgency indicators"""
        critical_words = ['emergency', 'urgent', 'critical', 'immediate', 'stat']
        high_words = ['important', 'priority', 'asap', 'soon']
        
        for word in critical_words:
            if word in text:
                return 'critical'
        
        for word in high_words:
            if word in text:
                return 'high'
        
        return 'medium'
    
    def _extract_task_type(self, text: str) -> Optional[str]:
        """Extract the type of task being requested"""
        task_patterns = {
            'admission': r'\b(admit|admission|admitting)\b',
            'discharge': r'\b(discharge|discharg)\b',
            'consultation': r'\b(consult|consultation|referral)\b',
            'procedure': r'\b(procedure|perform|conduct)\b',
            'documentation': r'\b(document|record|chart)\b',
            'assessment': r'\b(assess|evaluation|evaluate)\b',
            'training': r'\b(train|training|learn)\b',
            'maintenance': r'\b(maintain|maintenance|service)\b'
        }
        
        for task_type, pattern in task_patterns.items():
            if re.search(pattern, text):
                return task_type
        
        return None
    
    def _analyze_conversation_history(self, history: List[str]) -> Dict[str, any]:
        """Analyze conversation history to extract context"""
        combined_text = ' '.join(history).lower()
        
        keywords = self._extract_keywords(combined_text)
        category = self._determine_category(combined_text, keywords)
        department = self._determine_department(combined_text)
        
        return {
            'keywords': keywords,
            'category': category,
            'department': department
        }
    
    def rank_sops_by_relevance(self, context: SOPContext, sops: List) -> List[Tuple[any, float]]:
        """
        Rank SOPs by relevance to the given context
        
        Args:
            context: SOPContext object
            sops: List of SOP objects
            
        Returns:
            List of tuples (sop, relevance_score) sorted by relevance
        """
        scored_sops = []
        
        for sop in sops:
            score = self._calculate_relevance_score(context, sop)
            scored_sops.append((sop, score))
        
        # Sort by score in descending order
        scored_sops.sort(key=lambda x: x[1], reverse=True)
        
        return scored_sops
    
    def _calculate_relevance_score(self, context: SOPContext, sop) -> float:
        """Calculate relevance score between context and SOP"""
        score = 0.0
        
        # Category match (high weight)
        if context.category and context.category.lower() == sop.category.lower():
            score += 10.0
        
        # Department match (high weight)
        if context.department:
            if context.department.lower() in [d.lower() for d in sop.applicable_departments]:
                score += 8.0
        
        # Role match (medium weight)
        if context.role:
            if context.role.lower() in [r.lower() for r in sop.applicable_roles]:
                score += 5.0
        
        # Keyword matches (cumulative)
        sop_keywords = [k.lower() for k in sop.keywords]
        context_keywords = [k.lower() for k in context.keywords]
        keyword_matches = len(set(sop_keywords) & set(context_keywords))
        score += keyword_matches * 2.0
        
        # Priority match (low weight)
        if context.priority and context.priority == sop.priority:
            score += 2.0
        
        return score
