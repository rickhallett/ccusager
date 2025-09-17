"""Theme management system for dashboard"""

from typing import Dict, Any


class ThemeManager:
    """Manages visual themes for dashboard"""
    
    THEMES = {
        "monokai": {
            "primary": "#F8F8F2",
            "secondary": "#75715E",
            "accent": "#A6E22E",
            "warning": "#F92672",
            "error": "#F92672",
            "success": "#A6E22E",
            "info": "#66D9EF",
            "panel_border": "bright_black",
            "panel_title": "bright_cyan",
            "metric_value": "bright_cyan",
            "trend_up": "green",
            "trend_down": "red",
            "background": "#272822"
        },
        "dracula": {
            "primary": "#F8F8F2",
            "secondary": "#6272A4",
            "accent": "#8BE9FD",
            "warning": "#FFB86C",
            "error": "#FF5555",
            "success": "#50FA7B",
            "info": "#BD93F9",
            "panel_border": "purple",
            "panel_title": "bright_purple",
            "metric_value": "bright_cyan",
            "trend_up": "bright_green",
            "trend_down": "bright_red",
            "background": "#282A36"
        },
        "nord": {
            "primary": "#D8DEE9",
            "secondary": "#4C566A",
            "accent": "#88C0D0",
            "warning": "#D08770",
            "error": "#BF616A",
            "success": "#A3BE8C",
            "info": "#5E81AC",
            "panel_border": "blue",
            "panel_title": "bright_blue",
            "metric_value": "cyan",
            "trend_up": "green",
            "trend_down": "red",
            "background": "#2E3440"
        }
    }
    
    def __init__(self, theme_name: str = "monokai"):
        self.current_theme = theme_name
        self.theme = self.THEMES.get(theme_name, self.THEMES["monokai"])
    
    def set_theme(self, theme_name: str):
        """Switch to a different theme"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self.theme = self.THEMES[theme_name]
    
    def get_color(self, element: str) -> str:
        """Get color for specific element"""
        return self.theme.get(element, "white")
    
    def get_panel_border_style(self) -> str:
        """Get border style for panels"""
        return self.theme.get("panel_border", "white")
    
    def get_panel_title_style(self) -> str:
        """Get title style for panels"""
        return self.theme.get("panel_title", "bold")
    
    def get_metric_style(self) -> str:
        """Get style for metric values"""
        return self.theme.get("metric_value", "cyan")
    
    def get_trend_style(self, direction: str) -> str:
        """Get style for trend indicators"""
        if direction == "up":
            return self.theme.get("trend_up", "green")
        elif direction == "down":
            return self.theme.get("trend_down", "red")
        else:
            return self.theme.get("secondary", "dim")
    
    def apply_to_text(self, text: str, element: str) -> str:
        """Apply theme styling to text"""
        color = self.get_color(element)
        return f"[{color}]{text}[/{color}]"
    
    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return list(self.THEMES.keys())
    
    def export_theme(self) -> Dict[str, Any]:
        """Export current theme configuration"""
        return {
            "name": self.current_theme,
            "colors": self.theme.copy()
        }
    
    def import_custom_theme(self, name: str, theme_config: Dict[str, Any]):
        """Import a custom theme"""
        # Validate theme has required keys
        required_keys = ["primary", "panel_border", "metric_value"]
        if all(key in theme_config for key in required_keys):
            self.THEMES[name] = theme_config
            return True
        return False