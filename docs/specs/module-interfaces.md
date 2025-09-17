# CCUsager Module Interfaces

## Overview
This document defines the core module interfaces for CCUsager's 4 primary capabilities, designed for progressive enhancement and extensibility.

## Core Module Interfaces

### 1. Dashboard Module Interface (`IDashboardModule`)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DashboardPanel:
    """Represents a single dashboard panel"""
    id: str
    title: str
    type: str  # 'chart', 'metric', 'list', 'heatmap'
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
```

### 2. Alerts Module Interface (`IAlertsModule`)

```python
from enum import Enum

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertChannel(Enum):
    TERMINAL = "terminal"
    NOTIFICATION = "notification"
    WEBHOOK = "webhook"
    EMAIL = "email"
    SLACK = "slack"

@dataclass
class Alert:
    """Represents a single alert"""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    threshold_value: float
    current_value: float
    timestamp: datetime
    metadata: Dict[str, Any]

class IAlertsModule(ABC):
    """Interface for smart alerts functionality"""
    
    @abstractmethod
    def configure_threshold(self, 
                          metric: str, 
                          threshold: float, 
                          severity: AlertSeverity,
                          period: str = 'daily') -> str:
        """Configure alert threshold for a metric"""
        pass
    
    @abstractmethod
    def trigger_alert(self, alert: Alert) -> None:
        """Trigger an alert across configured channels"""
        pass
    
    @abstractmethod
    def add_channel(self, channel: AlertChannel, config: Dict[str, Any]) -> None:
        """Add notification channel"""
        pass
    
    @abstractmethod
    def remove_channel(self, channel: AlertChannel) -> bool:
        """Remove notification channel"""
        pass
    
    @abstractmethod
    def get_alert_history(self, 
                         limit: int = 100,
                         severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Retrieve alert history"""
        pass
    
    @abstractmethod
    def suppress_alert(self, alert_id: str, duration: int) -> None:
        """Temporarily suppress an alert"""
        pass
    
    @abstractmethod
    def test_channel(self, channel: AlertChannel) -> bool:
        """Test notification channel connectivity"""
        pass
```

### 3. Analysis Module Interface (`IAnalysisModule`)

```python
@dataclass
class Session:
    """Represents a Claude Code session"""
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    tokens_used: int
    cost: float
    model: str
    efficiency_score: Optional[float]
    metadata: Dict[str, Any]

@dataclass
class AnalysisResult:
    """Result of an analysis operation"""
    metric_name: str
    value: Any
    confidence: float
    insights: List[str]
    recommendations: List[str]
    visualizations: Optional[Dict[str, Any]]

class IAnalysisModule(ABC):
    """Interface for session analysis functionality"""
    
    @abstractmethod
    def analyze_session(self, session: Session) -> AnalysisResult:
        """Analyze a single session"""
        pass
    
    @abstractmethod
    def analyze_pattern(self, 
                       sessions: List[Session],
                       pattern_type: str) -> AnalysisResult:
        """Identify usage patterns across sessions"""
        pass
    
    @abstractmethod
    def calculate_efficiency(self, session: Session) -> float:
        """Calculate session efficiency score"""
        pass
    
    @abstractmethod
    def optimize_suggestions(self, 
                           sessions: List[Session]) -> List[Dict[str, Any]]:
        """Generate optimization suggestions"""
        pass
    
    @abstractmethod
    def forecast_usage(self, 
                      historical_data: List[Session],
                      days_ahead: int = 7) -> Dict[str, Any]:
        """Forecast future usage and costs"""
        pass
    
    @abstractmethod
    def compare_periods(self,
                       period1: tuple[datetime, datetime],
                       period2: tuple[datetime, datetime]) -> AnalysisResult:
        """Compare usage between two periods"""
        pass
    
    @abstractmethod
    def export_insights(self, format: str = 'json') -> str:
        """Export analysis insights"""
        pass
```

### 4. Reports Module Interface (`IReportsModule`)

```python
from enum import Enum

class ReportFormat(Enum):
    PDF = "pdf"
    HTML = "html"
    CSV = "csv"
    EXCEL = "excel"
    MARKDOWN = "markdown"
    JSON = "json"

@dataclass
class ReportSection:
    """Represents a section of a report"""
    title: str
    content: Any
    type: str  # 'text', 'chart', 'table', 'metric'
    order: int

class IReportsModule(ABC):
    """Interface for report generation functionality"""
    
    @abstractmethod
    def create_report(self, 
                     title: str,
                     period: tuple[datetime, datetime]) -> str:
        """Create a new report"""
        pass
    
    @abstractmethod
    def add_section(self, 
                   report_id: str,
                   section: ReportSection) -> None:
        """Add section to report"""
        pass
    
    @abstractmethod
    def add_chart(self,
                 report_id: str,
                 chart_type: str,
                 data: Any,
                 options: Dict[str, Any]) -> None:
        """Add chart to report"""
        pass
    
    @abstractmethod
    def export(self,
              report_id: str,
              format: ReportFormat,
              output_path: str,
              template: Optional[str] = None) -> str:
        """Export report to specified format"""
        pass
    
    @abstractmethod
    def schedule_report(self,
                       report_config: Dict[str, Any],
                       schedule: str) -> str:
        """Schedule automatic report generation"""
        pass
    
    @abstractmethod
    def get_templates(self) -> List[Dict[str, str]]:
        """Get available report templates"""
        pass
    
    @abstractmethod
    def preview(self, report_id: str) -> str:
        """Generate preview of report"""
        pass
```

## Integration Pattern

```python
class CCUsagerCore:
    """Main application core that integrates all modules"""
    
    def __init__(self):
        self.dashboard: Optional[IDashboardModule] = None
        self.alerts: Optional[IAlertsModule] = None
        self.analysis: Optional[IAnalysisModule] = None
        self.reports: Optional[IReportsModule] = None
    
    def register_module(self, module_type: str, module_instance: Any) -> None:
        """Register a module implementation"""
        if module_type == "dashboard":
            self.dashboard = module_instance
        elif module_type == "alerts":
            self.alerts = module_instance
        elif module_type == "analysis":
            self.analysis = module_instance
        elif module_type == "reports":
            self.reports = module_instance
    
    def is_module_available(self, module_type: str) -> bool:
        """Check if module is available"""
        return getattr(self, module_type, None) is not None
```

## Extension Points

Each interface provides clear extension points for:

1. **Custom Implementations**: Create alternative implementations of any module
2. **Plugin System**: Add functionality through plugin registration
3. **Data Sources**: Abstract data source interfaces for flexibility
4. **Rendering Engines**: Swap rendering backends (Rich, Textual, etc.)
5. **Export Formats**: Add new export formats without modifying core
6. **Analysis Algorithms**: Plug in different ML models or analysis methods
7. **Alert Channels**: Add new notification channels dynamically

## Progressive Enhancement Strategy

1. **Phase 1**: Implement core interfaces with basic functionality
2. **Phase 2**: Add advanced features through interface extensions
3. **Phase 3**: Enable plugin system for community contributions
4. **Phase 4**: Add async/streaming capabilities to interfaces

## Backward Compatibility

All interfaces follow these principles:
- Optional parameters with defaults for new features
- Deprecation warnings for changed methods
- Version-specific implementations can coexist
- Configuration migration utilities provided