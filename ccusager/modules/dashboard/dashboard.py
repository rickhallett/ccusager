"""Rich-based implementation of the Dashboard Module"""

from typing import Dict, Any, List, Optional
import time
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align

from ...interfaces import IDashboardModule, DashboardPanel
from .panel_renderer import PanelRenderer
from .data_source import CCUsageDataSource
from .theme_manager import ThemeManager


class RichDashboardModule(IDashboardModule):
    """Rich-based implementation of dashboard module"""
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.panels: Dict[str, DashboardPanel] = {}
        self.live_display: Optional[Live] = None
        self.refresh_rate = 5
        self.theme = "monokai"
        self.panel_renderer = PanelRenderer()
        self.data_source = CCUsageDataSource()
        self.theme_manager = ThemeManager()
        self._running = False
        self._setup_layout()
    
    def _setup_layout(self):
        """Initialize responsive grid layout"""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=2)
        )
        self.layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Initialize header
        self.layout["header"].update(
            Panel(
                Align.center("[bold cyan]CCUsager Dashboard[/bold cyan]", vertical="middle"),
                border_style="bright_blue"
            )
        )
        
        # Initialize footer
        self.layout["footer"].update(
            Panel(
                "[dim]Press 'q' to quit | 'r' to refresh | '?' for help[/dim]",
                border_style="dim"
            )
        )
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize dashboard with configuration"""
        # Apply configuration
        self.refresh_rate = config.get("refresh_rate", 5)
        self.theme = config.get("theme", "monokai")
        
        # Initialize default panels based on config
        default_panels = config.get("default_panels", [])
        for panel_config in default_panels:
            panel = DashboardPanel(**panel_config)
            self.add_panel(panel)
        
        # Apply theme
        self.theme_manager.set_theme(self.theme)
    
    def add_panel(self, panel: DashboardPanel) -> str:
        """Add a new panel to dashboard"""
        # Store panel
        self.panels[panel.id] = panel
        
        # Determine layout position
        self._position_panel(panel)
        
        # Initial render
        self._render_panel(panel)
        
        return panel.id
    
    def update_panel(self, panel_id: str, data: Any) -> None:
        """Update panel data"""
        if panel_id in self.panels:
            self.panels[panel_id].data = data
            self._render_panel(self.panels[panel_id])
    
    def remove_panel(self, panel_id: str) -> bool:
        """Remove panel from dashboard"""
        if panel_id in self.panels:
            del self.panels[panel_id]
            self._reorganize_layout()
            return True
        return False
    
    def render(self, theme: str = 'default') -> None:
        """Render dashboard to terminal"""
        if theme != 'default':
            self.theme = theme
            self.theme_manager.set_theme(theme)
        
        # Update all panels with latest data
        self._update_all_panels()
        
        # Render the layout
        self.console.print(self.layout)
    
    def set_refresh_rate(self, rate: int) -> None:
        """Set global refresh rate in seconds"""
        self.refresh_rate = max(1, min(60, rate))  # Clamp between 1-60 seconds
    
    def export_layout(self) -> Dict[str, Any]:
        """Export current layout configuration"""
        return {
            "theme": self.theme,
            "refresh_rate": self.refresh_rate,
            "panels": [
                {
                    "id": panel.id,
                    "title": panel.title,
                    "type": panel.type,
                    "position": panel.position,
                    "size": panel.size,
                    "refresh_rate": panel.refresh_rate
                }
                for panel in self.panels.values()
            ]
        }
    
    def start_live_mode(self):
        """Start live auto-refreshing mode"""
        self._running = True
        
        with Live(self.layout, refresh_per_second=1, console=self.console) as live:
            self.live_display = live
            
            while self._running:
                # Fetch latest data
                self._update_all_panels()
                
                # Update display
                live.update(self.layout)
                
                # Wait for refresh interval
                time.sleep(self.refresh_rate)
    
    def stop_live_mode(self):
        """Stop live mode"""
        self._running = False
    
    def _position_panel(self, panel: DashboardPanel):
        """Position panel in the layout grid"""
        # For Phase 1, simple left/right positioning based on panel count
        panel_count = len(self.panels)
        
        if panel_count % 2 == 1:
            target_layout = self.layout["main"]["left"]
        else:
            target_layout = self.layout["main"]["right"]
        
        # Create a sub-layout for this panel if needed
        if not hasattr(target_layout, "panels"):
            target_layout.panels = []
        
        target_layout.panels.append(panel.id)
    
    def _render_panel(self, panel: DashboardPanel):
        """Render individual panel"""
        rendered = self.panel_renderer.render(panel, self.theme_manager)
        
        # Determine which layout section to update
        panel_count = list(self.panels.keys()).index(panel.id) + 1
        
        if panel_count % 2 == 1:
            self.layout["main"]["left"].update(rendered)
        else:
            self.layout["main"]["right"].update(rendered)
    
    def _update_all_panels(self):
        """Update all panels with latest data"""
        # Fetch current data
        current_data = self.data_source.fetch_current_data()
        
        # Update each panel based on its type
        for panel in self.panels.values():
            panel_data = self._extract_panel_data(panel, current_data)
            self.update_panel(panel.id, panel_data)
    
    def _extract_panel_data(self, panel: DashboardPanel, raw_data: Dict[str, Any]) -> Any:
        """Extract relevant data for specific panel type"""
        if panel.type == "metric":
            # Extract metric value based on panel ID
            if panel.id == "cost":
                return {
                    "value": f"${raw_data.get('total_cost', 0):.2f}",
                    "trend": raw_data.get('cost_trend', 0)
                }
            elif panel.id == "tokens":
                return {
                    "value": f"{raw_data.get('total_tokens', 0):,}",
                    "trend": raw_data.get('token_trend', 0)
                }
            elif panel.id == "burn_rate":
                return {
                    "value": f"${raw_data.get('burn_rate', 0):.4f}/hr",
                    "trend": 0
                }
        elif panel.type == "chart":
            # Return trend data for charts
            return {
                "values": raw_data.get('trend_data', [])
            }
        
        return {}
    
    def _reorganize_layout(self):
        """Reorganize layout after panel removal"""
        # Re-render all remaining panels
        for panel in self.panels.values():
            self._render_panel(panel)