# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv가 없어도 계속 진행

# Management 모듈의 주요 컴포넌트들을 외부에서 쉽게 사용할 수 있도록 export

from .chains import (
    set_resource_planning_chain,
    set_search_planning_chain,
    set_summary_chain
)
from .models import get_openai_model
from .nodes import (
    ResourceManagementNode,
    IUResearchPlanNode,
    IUResearchSearchNode,
    IUResearchSummaryNode
)
from .state import ManagementState
from .tools import tavily_tool, TOOLS

__all__ = [
    # Chains
    "set_resource_planning_chain",
    "set_search_planning_chain", 
    "set_summary_chain",
    # Models
    "get_openai_model",
    # Nodes
    "ResourceManagementNode",
    "IUResearchPlanNode",
    "IUResearchSearchNode",
    "IUResearchSummaryNode",
    # State
    "ManagementState",
    # Tools
    "tavily_tool",
    "TOOLS"
]
