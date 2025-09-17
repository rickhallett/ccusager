"""Panel rendering system for the dashboard"""

from typing import Any, List
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn

from ...interfaces import DashboardPanel


class PanelRenderer:
    """Handles rendering different panel types"""
    
    def render(self, panel: DashboardPanel, theme_manager: Any) -> Panel:
        """Render panel based on its type"""
        if panel.type == "metric":
            return self.render_metric_panel(panel, theme_manager)
        elif panel.type == "chart":
            return self.render_chart_panel(panel, theme_manager)
        elif panel.type == "list":
            return self.render_list_panel(panel, theme_manager)
        elif panel.type == "heatmap":
            return self.render_heatmap_panel(panel, theme_manager)
        elif panel.type == "gauge":
            return self.render_gauge_panel(panel, theme_manager)
        elif panel.type == "status":
            return self.render_status_panel(panel, theme_manager)
        else:
            return self.render_default_panel(panel, theme_manager)
    
    def render_metric_panel(self, panel: DashboardPanel, theme_manager: Any) -> Panel:
        """Render simple metric display"""
        value = panel.data.get('value', '0')
        trend = panel.data.get('trend', 0)
        
        # Build content with trend indicator
        content = Text()
        content.append(str(value), style="bold cyan")
        
        if trend > 0:
            content.append(f" ↑{trend}%", style="green")
        elif trend < 0:
            content.append(f" ↓{abs(trend)}%", style="red")
        
        # Apply theme styling
        border_style = theme_manager.get_panel_border_style()
        
        return Panel(
            Align.center(content, vertical="middle"),
            title=f"[bold]{panel.title}[/bold]",
            border_style=border_style,
            height=5
        )
    
    def render_chart_panel(self, panel: DashboardPanel, theme_manager: Any) -> Panel:
        """Render sparkline chart"""
        data_points = panel.data.get('values', [])
        
        if not data_points:
            sparkline = "[dim]No data available[/dim]"
        else:
            sparkline = self._create_sparkline(data_points)
        
        border_style = theme_manager.get_panel_border_style()
        
        return Panel(
            Align.center(sparkline, vertical="middle"),
            title=f"[bold]{panel.title}[/bold]",
            border_style=border_style,
            height=5
        )
    
    def render_list_panel(self, panel: DashboardPanel, theme_manager: Any) -> Panel:
        """Render list of items"""
        items = panel.data.get('items', [])
        
        table = Table(show_header=False, box=None, padding=0)
        
        for item in items[:5]:  # Show max 5 items
            table.add_row(f"• {item}")
        
        border_style = theme_manager.get_panel_border_style()
        
        return Panel(
            table,
            title=f"[bold]{panel.title}[/bold]",
            border_style=border_style
        )
    
    def render_heatmap_panel(self, panel: DashboardPanel, theme_manager: Any) -> Panel:
        """Render heatmap visualization"""
        data = panel.data.get('matrix', [])
        
        # Simple ASCII heatmap
        heatmap = self._create_heatmap(data)
        
        border_style = theme_manager.get_panel_border_style()
        
        return Panel(
            heatmap,
            title=f"[bold]{panel.title}[/bold]",
            border_style=border_style
        )
    
    def render_gauge_panel(self, panel: DashboardPanel, theme_manager: Any) -> Panel:
        """Render gauge/progress indicator"""
        value = panel.data.get('value', 0)
        max_value = panel.data.get('max', 100)
        
        # Create progress bar
        progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        
        task_id = progress.add_task("", completed=value, total=max_value)
        
        border_style = theme_manager.get_panel_border_style()
        
        return Panel(
            progress,
            title=f"[bold]{panel.title}[/bold]",
            border_style=border_style,
            height=5
        )
    
    def render_status_panel(self, panel: DashboardPanel, theme_manager: Any) -> Panel:
        """Render status indicator"""
        status = panel.data.get('status', 'unknown')
        message = panel.data.get('message', '')
        
        # Status colors
        status_colors = {
            'online': 'green',
            'offline': 'red',
            'warning': 'yellow',
            'error': 'red bold',
            'unknown': 'dim'
        }
        
        color = status_colors.get(status, 'white')
        
        content = Text()
        content.append("●", style=color)
        content.append(f" {status.upper()}", style=color)
        if message:
            content.append(f"\n{message}", style="dim")
        
        border_style = theme_manager.get_panel_border_style()
        
        return Panel(
            Align.center(content, vertical="middle"),
            title=f"[bold]{panel.title}[/bold]",
            border_style=border_style,
            height=5
        )
    
    def render_default_panel(self, panel: DashboardPanel, theme_manager: Any) -> Panel:
        """Render default panel for unknown types"""
        border_style = theme_manager.get_panel_border_style()
        
        return Panel(
            f"[dim]Panel type '{panel.type}' not implemented[/dim]",
            title=f"[bold]{panel.title}[/bold]",
            border_style=border_style
        )
    
    def _create_sparkline(self, data_points: List[float]) -> str:
        """Create ASCII sparkline from data points"""
        if not data_points:
            return ""
        
        # Normalize data to 0-7 range for sparkline characters
        min_val = min(data_points)
        max_val = max(data_points)
        
        if max_val == min_val:
            # All values are the same
            return "─" * len(data_points)
        
        # Sparkline characters from low to high
        sparks = " ▁▂▃▄▅▆▇█"
        
        sparkline = ""
        for value in data_points:
            # Normalize to 0-8 range
            normalized = int(((value - min_val) / (max_val - min_val)) * 8)
            sparkline += sparks[normalized]
        
        return sparkline
    
    def _create_heatmap(self, matrix: List[List[float]]) -> str:
        """Create ASCII heatmap from matrix data"""
        if not matrix:
            return "[dim]No data[/dim]"
        
        # Heatmap characters from cold to hot
        heat_chars = " ░▒▓█"
        
        heatmap_lines = []
        for row in matrix:
            line = ""
            for value in row:
                # Normalize value to 0-4 range
                normalized = min(4, max(0, int(value * 4)))
                line += heat_chars[normalized]
            heatmap_lines.append(line)
        
        return "\n".join(heatmap_lines)