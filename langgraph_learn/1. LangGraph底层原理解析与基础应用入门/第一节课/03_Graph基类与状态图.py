# -*- coding: utf-8 -*-
"""
【案例 3】Graph 基类与 StateGraph
============================================

本案例展示 LangGraph 中 Graph 基类的核心结构

要点：
1. Graph 类的核心属性（nodes, edges, branches）
2. StateGraph 状态图的概念
3. TypedDict 定义状态模式
"""

# ============================================================
# 1. Graph 基类结构
# ============================================================
from collections import defaultdict
from typing import Any, Callable, Dict, Optional, Set, Tuple, Union, Awaitable, Hashable

class Graph:
    """LangGraph Graph 基类源码结构展示"""
    def __init__(self) -> None:
        self.nodes: Dict[str, Any] = {}           # 存储图中所有节点
        self.edges: Set[Tuple[str, str]] = set()   # 存储图中所有边
        self.branches: defaultdict = defaultdict(dict)  # 条件分支
        self.support_multiple_edges = False         # 是否支持多重边
        self.compiled = False                      # 图是否已编译

    def add_node(self, node: Union[str, Callable], action: Optional[Callable] = None, *, metadata: Optional[Dict[str, Any]] = None) -> 'Graph':
        """添加新节点到图中"""
        pass

    def add_edge(self, start_key: str, end_key: str) -> 'Graph':
        """添加边连接两个节点"""
        pass

    def add_conditional_edges(self, source: str, path: Callable, path_map: Optional[Dict[Hashable, str]] = None, then: Optional[str] = None) -> 'Graph':
        """添加条件边"""
        pass

    def set_entry_point(self, key: str) -> 'Graph':
        """设置入口点"""
        pass

    def set_finish_point(self, key: str) -> 'Graph':
        """设置结束点"""
        pass

    def compile(self, checkpointer=None, interrupt_before: Optional[Set[str]] = None, interrupt_after: Optional[Set[str]] = None, debug: bool = False) -> 'Graph':
        """编译图"""
        pass

# ============================================================
# 2. StateGraph 状态图
# ============================================================
from typing_extensions import TypedDict

class StateGraph(Graph):
    """StateGraph 状态图 - 管理状态并支持状态转换的图"""
    def __init__(self, state_schema: Optional[Type[Any]] = None, config_schema: Optional[Type[Any]] = None) -> None:
        super().__init__()
        self.state_schema = state_schema      # 图状态的结构定义
        self.config_schema = config_schema    # 配置结构定义
        self.nodes: Dict[str, Any] = {}       # 节点存储
        self.edges: Set[Tuple[str, str]] = set()   # 边存储
        self.branches: defaultdict = defaultdict(dict)   # 条件分支

# ============================================================
# 3. TypedDict 定义状态
# ============================================================
class InputState(TypedDict):
    """输入状态定义"""
    question: str

class OutputState(TypedDict):
    """输出状态定义"""
    answer: str

class OverallState(InputState, OutputState):
    """合并输入输出状态"""
    pass

print("=" * 50)
print("案例 3: Graph 基类与 StateGraph")
print("=" * 50)
print(f"Graph 类核心属性: nodes, edges, branches, compiled")
print(f"StateGraph 继承自 Graph，增加了状态管理能力")
print(f"TypedDict 用于定义状态模式，确保类型安全")