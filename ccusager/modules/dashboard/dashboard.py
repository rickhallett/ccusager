"""Rich-based implementation of the Dashboard Module"""

from typing import Dict, Any, List, Optional
import time
import json
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

from ...interfaces import IDashboardModule, DashboardPanel
from .panel_renderer import PanelRenderer
from .data_source import CCUsageDataSource
from .theme_manager import ThemeManager
from .keyboard_handler import DashboardKeyboardHandler


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
        self.keyboard_handler = DashboardKeyboardHandler(self)
        self._running = False
        self._last_update = 0
        self._status_message = ""
        self._show_help = None
        self._export_pending = None
        self._setup_layout()
    
    def _setup_layout(self):
        """Initialize responsive grid layout"""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=2)
        )
        
        # Split main into a 2x2 grid to better accommodate 7 panels
        self.layout["main"].split_row(
            Layout(name="left_column"),
            Layout(name="right_column")
        )
        
        # Split each column into sections
        self.layout["main"]["left_column"].split_column(
            Layout(name="left_top"),
            Layout(name="left_middle"),
            Layout(name="left_bottom")
        )
        
        self.layout["main"]["right_column"].split_column(
            Layout(name="right_top"),
            Layout(name="right_middle"),
            Layout(name="right_bottom")
        )
        
        # Initialize header
        self.layout["header"].update(
            Panel(
                Align.center("[bold cyan]CCUsager Dashboard[/bold cyan]", vertical="middle"),
                border_style="bright_blue"
            )
        )
        
        # Initialize footer with keyboard shortcuts
        self._update_footer()
    
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
        """Start live auto-refreshing mode with keyboard interaction"""
        self._running = True
        
        # Start keyboard listener
        self.keyboard_handler.start_listening()
        
        try:
            with Live(self.layout, refresh_per_second=2, console=self.console) as live:
                self.live_display = live
                
                while self._running:
                    current_time = time.time()
                    
                    # Check if it's time to refresh (unless paused)
                    if not self.keyboard_handler.is_paused():
                        if current_time - self._last_update >= self.refresh_rate:
                            self._update_all_panels()
                            self._last_update = current_time
                    
                    # Handle help display
                    if self._show_help:
                        self._display_help()
                    
                    # Handle export
                    if self._export_pending:
                        self._save_config(self._export_pending)
                        self._export_pending = None
                    
                    # Update footer with status
                    self._update_footer()
                    
                    # Update display
                    live.update(self.layout)
                    
                    # Short sleep to prevent CPU spinning
                    time.sleep(0.1)
        finally:
            # Stop keyboard listener when exiting
            self.keyboard_handler.stop_listening()
    
    def stop_live_mode(self):
        """Stop live mode"""
        self._running = False
    
    def _position_panel(self, panel: DashboardPanel):
        """Position panel in the layout grid"""
        # Map panel positions to layout sections
        panel_count = len(self.panels)
        
        # Define layout sections in order
        layout_sections = [
            "left_top",
            "right_top", 
            "left_middle",
            "right_middle",
            "left_bottom",
            "right_bottom"
        ]
        
        # Assign panel to available section
        if panel_count <= len(layout_sections):
            section_name = layout_sections[panel_count - 1]
            # Store the section assignment for this panel
            if not hasattr(self, '_panel_sections'):
                self._panel_sections = {}
            self._panel_sections[panel.id] = section_name
    
    def _render_panel(self, panel: DashboardPanel):
        """Render individual panel"""
        rendered = self.panel_renderer.render(panel, self.theme_manager)
        
        # Get the assigned section for this panel
        if hasattr(self, '_panel_sections') and panel.id in self._panel_sections:
            section_name = self._panel_sections[panel.id]
            
            # Navigate to the correct layout section
            try:
                if section_name.startswith("left_"):
                    column = "left_column"
                    section = section_name
                else:
                    column = "right_column" 
                    section = section_name
                
                self.layout["main"][column][section].update(rendered)
            except KeyError:
                # Fallback to left column if section not found
                self.layout["main"]["left_column"]["left_top"].update(rendered)
        else:
            # Fallback positioning
            self.layout["main"]["left_column"]["left_top"].update(rendered)
    
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
            # Extract metric value and sparkline based on panel ID
            if panel.id == "cost":
                return {
                    "value": f"${raw_data.get('total_cost', 0):.2f}",
                    "trend": raw_data.get('cost_trend', 0),
                    "sparkline": self.data_source.get_metric_sparkline('cost')
                }
            elif panel.id == "tokens":
                return {
                    "value": f"{raw_data.get('total_tokens', 0):,}",
                    "trend": raw_data.get('token_trend', 0),
                    "sparkline": self.data_source.get_metric_sparkline('tokens')
                }
            elif panel.id == "burn_rate":
                return {
                    "value": f"${raw_data.get('burn_rate', 0):.4f}/hr",
                    "trend": 0,
                    "sparkline": self.data_source.get_metric_sparkline('burn_rate')
                }
            elif panel.id == "efficiency":
                efficiency = self.data_source.metric_history.get('efficiency', [0])[-1]
                return {
                    "value": f"{efficiency:.1f}%",
                    "trend": 0,
                    "sparkline": self.data_source.get_metric_sparkline('efficiency')
                }
        elif panel.type == "chart":
            # Return trend data for charts
            return {
                "values": raw_data.get('trend_data', [])
            }
        elif panel.type == "distribution":
            # Model distribution data
            return {
                "distribution": raw_data.get('model_distribution', {}),
                "total_uses": sum(self.data_source.cache.get('model_usage', {}).values())
            }
        elif panel.type == "gauge":
            # Context window utilization
            if panel.id == "context_util":
                return {
                    "value": raw_data.get('context_utilization', 0),
                    "max": 100,
                    "label": "Context Window"
                }
        
        return {}
    
    def _reorganize_layout(self):
        """Reorganize layout after panel removal"""
        # Re-render all remaining panels
        for panel in self.panels.values():
            self._render_panel(panel)
    
    def _update_footer(self):
        """Update footer with current status and shortcuts"""
        footer_text = "[dim]"
        
        # Add status message if present
        if self._status_message:
            footer_text += f"[bold yellow]{self._status_message}[/bold yellow] | "
            # Clear status message after displaying
            if time.time() - self._last_update > 2:
                self._status_message = ""
        
        # Add pause indicator
        if self.keyboard_handler.is_paused():
            footer_text += "[bold red]PAUSED[/bold red] | "
        
        # Add keyboard shortcuts
        footer_text += "q: Quit | r: Refresh | ?: Help | p: Pause | t: Theme | +/-: Speed"
        footer_text += "[/dim]"
        
        self.layout["footer"].update(
            Panel(
                footer_text,
                border_style="dim"
            )
        )
    
    def _display_help(self):
        """Display help overlay in main panel"""
        help_text = self.keyboard_handler.get_help_text()
        
        help_panel = Panel(
            Align.center(help_text, vertical="middle"),
            title="[bold]Keyboard Shortcuts[/bold]",
            border_style="bright_cyan"
        )
        
        # Temporarily replace main content with help
        self.layout["main"].update(help_panel)
        
        # Clear help flag after a delay
        if time.time() - self._last_update > 3:
            self._show_help = None
            # Re-render panels
            for panel in self.panels.values():
                self._render_panel(panel)
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        config_path = Path.home() / ".ccusager" / "dashboard_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self._status_message = f"Config saved to {config_path}"