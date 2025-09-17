"""Core module interfaces for CCUsager"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass
class DashboardPanel:
    """Represents a single dashboard panel"""
    id: str
    title: str
    type: str  # 'chart', 'metric', 'list', 'heatmap', 'gauge', 'status'
    position: tuple[int, int]
    size: tuple[int, int]
    data: Any
    refresh_rate: int = 5


class IDashboardModule(ABC):
    """Interface for real-time dashboard functionality"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize dashboard with configuration"""
        pass
    
    @abstractmethod
    def add_panel(self, panel: DashboardPanel) -> str:
        """Add a new panel to dashboard"""
        pass
    
    @abstractmethod
    def update_panel(self, panel_id: str, data: Any) -> None:
        """Update panel data"""
        pass
    
    @abstractmethod
    def remove_panel(self, panel_id: str) -> bool:
        """Remove panel from dashboard"""
        pass
    
    @abstractmethod
    def render(self, theme: str = 'default') -> None:
        """Render dashboard to terminal"""
        pass
    
    @abstractmethod
    def set_refresh_rate(self, rate: int) -> None:
        """Set global refresh rate in seconds"""
        pass
    
    @abstractmethod
    def export_layout(self) -> Dict[str, Any]:
        """Export current layout configuration"""
        pass