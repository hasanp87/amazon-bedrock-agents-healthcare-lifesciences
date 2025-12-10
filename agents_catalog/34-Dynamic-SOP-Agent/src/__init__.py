"""
Dynamic SOP Agent - Context-aware Standard Operating Procedure assistant
"""

__version__ = "1.0.0"

# Lazy imports to avoid requiring strands for utility modules
def _lazy_import():
    from .agents.dynamic_sop_agent import DynamicSOPAgent
    from .models.sop_models import SOP, SOPStep, SOPMetadata, SOPContext, SOPRepository
    from .utils.sop_loader import SOPLoader
    from .utils.context_analyzer import ContextAnalyzer
    from .utils.mcp_connector import MCPConnector
    
    return {
        'DynamicSOPAgent': DynamicSOPAgent,
        'SOP': SOP,
        'SOPStep': SOPStep,
        'SOPMetadata': SOPMetadata,
        'SOPContext': SOPContext,
        'SOPRepository': SOPRepository,
        'SOPLoader': SOPLoader,
        'ContextAnalyzer': ContextAnalyzer,
        'MCPConnector': MCPConnector
    }

__all__ = [
    'DynamicSOPAgent',
    'SOP',
    'SOPStep',
    'SOPMetadata',
    'SOPContext',
    'SOPRepository',
    'SOPLoader',
    'ContextAnalyzer',
    'MCPConnector'
]
