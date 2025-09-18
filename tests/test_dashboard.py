"""Tests for the Real-time Dashboard Module"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time

from ccusager.interfaces import DashboardPanel
from ccusager.modules.dashboard import RichDashboardModule
from ccusager.modules.dashboard.data_source import CCUsageDataSource
from ccusager.modules.dashboard.panel_renderer import PanelRenderer
from ccusager.modules.dashboard.theme_manager import ThemeManager
from ccusager.modules.dashboard.keyboard_handler import KeyboardHandler, DashboardKeyboardHandler


class TestDashboardModule(unittest.TestCase):
    """Test cases for RichDashboardModule"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dashboard = RichDashboardModule()
        
    def test_initialization(self):
        """Test dashboard initialization"""
        self.assertIsNotNone(self.dashboard.console)
        self.assertIsNotNone(self.dashboard.layout)
        self.assertEqual(self.dashboard.refresh_rate, 5)
        self.assertEqual(self.dashboard.theme, "monokai")
        self.assertIsInstance(self.dashboard.panels, dict)
        
    def test_add_panel(self):
        """Test adding panels to dashboard"""
        panel = DashboardPanel(
            id="test_panel",
            title="Test Panel",
            type="metric",
            position=(0, 0),
            size=(1, 1),
            data={"value": "100"},
            refresh_rate=5
        )
        
        panel_id = self.dashboard.add_panel(panel)
        self.assertEqual(panel_id, "test_panel")
        self.assertIn("test_panel", self.dashboard.panels)
        
    def test_update_panel(self):
        """Test updating panel data"""
        # Add a panel first
        panel = DashboardPanel(
            id="test_panel",
            title="Test Panel",
            type="metric",
            position=(0, 0),
            size=(1, 1),
            data={"value": "100"},
            refresh_rate=5
        )
        self.dashboard.add_panel(panel)
        
        # Update the panel
        new_data = {"value": "200"}
        self.dashboard.update_panel("test_panel", new_data)
        
        self.assertEqual(self.dashboard.panels["test_panel"].data, new_data)
        
    def test_remove_panel(self):
        """Test removing panels"""
        panel = DashboardPanel(
            id="test_panel",
            title="Test Panel",
            type="metric",
            position=(0, 0),
            size=(1, 1),
            data={},
            refresh_rate=5
        )
        
        self.dashboard.add_panel(panel)
        result = self.dashboard.remove_panel("test_panel")
        
        self.assertTrue(result)
        self.assertNotIn("test_panel", self.dashboard.panels)
        
    def test_set_refresh_rate(self):
        """Test setting refresh rate"""
        self.dashboard.set_refresh_rate(10)
        self.assertEqual(self.dashboard.refresh_rate, 10)
        
        # Test clamping
        self.dashboard.set_refresh_rate(0)
        self.assertEqual(self.dashboard.refresh_rate, 1)
        
        self.dashboard.set_refresh_rate(100)
        self.assertEqual(self.dashboard.refresh_rate, 60)
        
    def test_export_layout(self):
        """Test exporting layout configuration"""
        config = self.dashboard.export_layout()
        
        self.assertIn("theme", config)
        self.assertIn("refresh_rate", config)
        self.assertIn("panels", config)
        self.assertEqual(config["theme"], "monokai")
        self.assertEqual(config["refresh_rate"], 5)


class TestDataSource(unittest.TestCase):
    """Test cases for CCUsageDataSource"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.data_source = CCUsageDataSource()
        self.data_source.mock_mode = True  # Use mock data for testing
        
    def test_fetch_current_data(self):
        """Test fetching current data"""
        data = self.data_source.fetch_current_data()
        
        self.assertIsInstance(data, dict)
        self.assertIn("total_cost", data)
        self.assertIn("total_tokens", data)
        self.assertIn("burn_rate", data)
        
    def test_metric_history(self):
        """Test metric history tracking"""
        # Fetch data multiple times to build history
        for _ in range(5):
            self.data_source.fetch_current_data()
            time.sleep(0.1)
        
        # Check that history is being maintained
        cost_history = self.data_source.get_metric_sparkline('cost')
        self.assertIsInstance(cost_history, list)
        self.assertTrue(len(cost_history) > 0)
        
    def test_model_distribution(self):
        """Test model distribution calculation"""
        # Add some mock model usage
        self.data_source.cache['model_usage'] = {
            'claude-3-opus': 10,
            'claude-3-sonnet': 5,
            'claude-3-haiku': 5
        }
        
        distribution = self.data_source.get_model_distribution()
        
        self.assertIn('claude-3-opus', distribution)
        self.assertEqual(distribution['claude-3-opus'], 50.0)  # 10/20 = 50%
        
    def test_calculate_burn_rate(self):
        """Test burn rate calculation"""
        # Set up trend data
        current_time = time.time()
        self.data_source.cache['trends'] = [
            {'timestamp': current_time - 3600, 'cost': 10, 'tokens': 1000},
            {'timestamp': current_time - 1800, 'cost': 15, 'tokens': 1500},
            {'timestamp': current_time, 'cost': 20, 'tokens': 2000}
        ]
        
        burn_rate = self.data_source.calculate_burn_rate()
        self.assertGreaterEqual(burn_rate, 0)


class TestPanelRenderer(unittest.TestCase):
    """Test cases for PanelRenderer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.renderer = PanelRenderer()
        self.theme_manager = ThemeManager()
        
    def test_render_metric_panel(self):
        """Test rendering metric panel"""
        panel = DashboardPanel(
            id="test",
            title="Test Metric",
            type="metric",
            position=(0, 0),
            size=(1, 1),
            data={
                "value": "$100.00",
                "trend": 5.0,
                "sparkline": [1, 2, 3, 4, 5]
            },
            refresh_rate=5
        )
        
        result = self.renderer.render_metric_panel(panel, self.theme_manager)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "[bold]Test Metric[/bold]")
        
    def test_render_distribution_panel(self):
        """Test rendering distribution panel"""
        panel = DashboardPanel(
            id="test",
            title="Model Distribution",
            type="distribution",
            position=(0, 0),
            size=(1, 1),
            data={
                "distribution": {
                    "model-1": 60,
                    "model-2": 30,
                    "model-3": 10
                },
                "total_uses": 100
            },
            refresh_rate=5
        )
        
        result = self.renderer.render_distribution_panel(panel, self.theme_manager)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "[bold]Model Distribution[/bold]")
        
    def test_sparkline_creation(self):
        """Test sparkline generation"""
        data_points = [1, 2, 3, 4, 5, 4, 3, 2, 1]
        sparkline = self.renderer._create_sparkline(data_points)
        
        self.assertIsInstance(sparkline, str)
        self.assertTrue(len(sparkline) > 0)


class TestKeyboardHandler(unittest.TestCase):
    """Test cases for keyboard handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_dashboard = Mock()
        self.mock_dashboard.refresh_rate = 5
        self.mock_dashboard.theme = "monokai"
        self.mock_dashboard.theme_manager = Mock()
        self.mock_dashboard.theme_manager.get_available_themes.return_value = ["monokai", "dracula", "nord"]
        self.mock_dashboard.export_layout.return_value = {"test": "config"}
        
        self.handler = DashboardKeyboardHandler(self.mock_dashboard)
        
    def test_key_binding_registration(self):
        """Test that default key bindings are registered"""
        self.assertIn('q', self.handler.key_bindings)
        self.assertIn('r', self.handler.key_bindings)
        self.assertIn('?', self.handler.key_bindings)
        self.assertIn('p', self.handler.key_bindings)
        self.assertIn('t', self.handler.key_bindings)
        
    def test_pause_toggle(self):
        """Test pause/resume functionality"""
        self.assertFalse(self.handler.is_paused())
        
        self.handler.toggle_pause()
        self.assertTrue(self.handler.is_paused())
        
        self.handler.toggle_pause()
        self.assertFalse(self.handler.is_paused())
        
    def test_refresh_rate_adjustment(self):
        """Test increasing and decreasing refresh rate"""
        self.handler.increase_refresh_rate()
        self.mock_dashboard.set_refresh_rate.assert_called_with(4)
        
        self.mock_dashboard.refresh_rate = 5
        self.handler.decrease_refresh_rate()
        self.mock_dashboard.set_refresh_rate.assert_called_with(6)
        
    def test_theme_cycling(self):
        """Test theme cycling"""
        self.handler.cycle_theme()
        
        # Should set to next theme (dracula)
        self.assertEqual(self.mock_dashboard.theme, "dracula")
        self.mock_dashboard.theme_manager.set_theme.assert_called_with("dracula")
        
    def test_help_text_generation(self):
        """Test help text generation"""
        help_text = self.handler.get_help_text()
        
        self.assertIn("Keyboard Shortcuts", help_text)
        self.assertIn("q", help_text)
        self.assertIn("Quit", help_text)


class TestThemeManager(unittest.TestCase):
    """Test cases for ThemeManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.theme_manager = ThemeManager()
        
    def test_default_theme(self):
        """Test default theme is monokai"""
        self.assertEqual(self.theme_manager.current_theme, "monokai")
        
    def test_set_theme(self):
        """Test setting different themes"""
        self.theme_manager.set_theme("dracula")
        self.assertEqual(self.theme_manager.current_theme, "dracula")
        
        self.theme_manager.set_theme("nord")
        self.assertEqual(self.theme_manager.current_theme, "nord")
        
    def test_get_available_themes(self):
        """Test getting list of available themes"""
        themes = self.theme_manager.get_available_themes()
        
        self.assertIn("monokai", themes)
        self.assertIn("dracula", themes)
        self.assertIn("nord", themes)
        
    def test_theme_colors(self):
        """Test theme color retrieval"""
        color = self.theme_manager.get_color("primary")
        self.assertIsNotNone(color)
        
        border_style = self.theme_manager.get_panel_border_style()
        self.assertIsNotNone(border_style)


if __name__ == "__main__":
    unittest.main()