"""Keyboard event handling for dashboard interaction"""

import threading
import sys
import termios
import tty
from typing import Callable, Dict, Optional
from contextlib import contextmanager


class KeyboardHandler:
    """Handles keyboard input for dashboard interaction"""
    
    def __init__(self):
        self.key_bindings: Dict[str, Callable] = {}
        self.running = False
        self.listener_thread: Optional[threading.Thread] = None
        self._original_settings = None
        
    def register_key(self, key: str, callback: Callable, description: str = ""):
        """Register a keyboard shortcut"""
        self.key_bindings[key] = callback
        if hasattr(callback, '__doc__'):
            callback.__doc__ = description or callback.__doc__
    
    def unregister_key(self, key: str):
        """Remove a keyboard shortcut"""
        if key in self.key_bindings:
            del self.key_bindings[key]
    
    @contextmanager
    def raw_mode(self):
        """Context manager for raw terminal mode"""
        if sys.platform == 'win32':
            # Windows doesn't support termios
            yield
            return
            
        try:
            # Save original terminal settings
            self._original_settings = termios.tcgetattr(sys.stdin)
            
            # Set terminal to raw mode
            tty.setraw(sys.stdin.fileno())
            yield
        finally:
            # Restore original settings
            if self._original_settings:
                termios.tcsetattr(
                    sys.stdin.fileno(),
                    termios.TCSADRAIN,
                    self._original_settings
                )
    
    def start_listening(self):
        """Start listening for keyboard input in a separate thread"""
        if self.running:
            return
        
        self.running = True
        self.listener_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self.listener_thread.start()
    
    def stop_listening(self):
        """Stop listening for keyboard input"""
        self.running = False
        if self.listener_thread:
            self.listener_thread.join(timeout=0.5)
    
    def _listen_loop(self):
        """Main keyboard listening loop"""
        with self.raw_mode():
            while self.running:
                try:
                    # Read single character
                    char = sys.stdin.read(1)
                    
                    if char in self.key_bindings:
                        # Execute registered callback
                        callback = self.key_bindings[char]
                        callback()
                    
                    # Special handling for common keys
                    if char == '\x03':  # Ctrl+C
                        self.running = False
                        break
                    elif char == '\x1b':  # ESC
                        # Handle escape sequences (arrow keys, etc.)
                        self._handle_escape_sequence()
                        
                except (KeyboardInterrupt, EOFError):
                    self.running = False
                    break
                except Exception:
                    # Silently ignore other exceptions to keep loop running
                    pass
    
    def _handle_escape_sequence(self):
        """Handle multi-character escape sequences like arrow keys"""
        try:
            # Read next characters for escape sequence
            next_char = sys.stdin.read(1)
            if next_char == '[':
                # ANSI escape sequence
                final_char = sys.stdin.read(1)
                
                # Map arrow keys to actions
                arrow_keys = {
                    'A': 'up',
                    'B': 'down',
                    'C': 'right',
                    'D': 'left'
                }
                
                if final_char in arrow_keys:
                    key_name = f"arrow_{arrow_keys[final_char]}"
                    if key_name in self.key_bindings:
                        self.key_bindings[key_name]()
        except:
            pass
    
    def get_help_text(self) -> str:
        """Generate help text for available keyboard shortcuts"""
        help_lines = ["Keyboard Shortcuts:", "=" * 40]
        
        # Standard shortcuts
        standard_keys = {
            'q': 'Quit dashboard',
            'r': 'Refresh data',
            '?': 'Show this help',
            'h': 'Show this help',
            'p': 'Pause/Resume auto-refresh',
            't': 'Cycle through themes',
            '+': 'Increase refresh rate',
            '-': 'Decrease refresh rate',
            'e': 'Export configuration',
            'c': 'Clear and redraw'
        }
        
        for key, desc in standard_keys.items():
            if key in self.key_bindings:
                help_lines.append(f"  {key:<3} - {desc}")
        
        # Arrow keys
        if any(k.startswith('arrow_') for k in self.key_bindings):
            help_lines.append("\nNavigation:")
            help_lines.append("  ↑↓←→ - Navigate panels")
        
        return "\n".join(help_lines)


class DashboardKeyboardHandler(KeyboardHandler):
    """Specialized keyboard handler for dashboard operations"""
    
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard
        self.paused = False
        self.setup_default_bindings()
    
    def setup_default_bindings(self):
        """Set up default keyboard bindings for dashboard"""
        
        # Quit
        self.register_key('q', self.quit_dashboard, "Quit dashboard")
        self.register_key('Q', self.quit_dashboard, "Quit dashboard")
        
        # Refresh
        self.register_key('r', self.refresh_data, "Refresh data immediately")
        self.register_key('R', self.refresh_data, "Refresh data immediately")
        
        # Help
        self.register_key('?', self.show_help, "Show keyboard shortcuts")
        self.register_key('h', self.show_help, "Show keyboard shortcuts")
        self.register_key('H', self.show_help, "Show keyboard shortcuts")
        
        # Pause/Resume
        self.register_key('p', self.toggle_pause, "Pause/Resume auto-refresh")
        self.register_key('P', self.toggle_pause, "Pause/Resume auto-refresh")
        self.register_key(' ', self.toggle_pause, "Pause/Resume auto-refresh")
        
        # Theme cycling
        self.register_key('t', self.cycle_theme, "Cycle through themes")
        self.register_key('T', self.cycle_theme, "Cycle through themes")
        
        # Refresh rate adjustment
        self.register_key('+', self.increase_refresh_rate, "Increase refresh rate")
        self.register_key('=', self.increase_refresh_rate, "Increase refresh rate")
        self.register_key('-', self.decrease_refresh_rate, "Decrease refresh rate")
        self.register_key('_', self.decrease_refresh_rate, "Decrease refresh rate")
        
        # Export
        self.register_key('e', self.export_config, "Export configuration")
        self.register_key('E', self.export_config, "Export configuration")
        
        # Clear screen
        self.register_key('c', self.clear_screen, "Clear and redraw")
        self.register_key('C', self.clear_screen, "Clear and redraw")
    
    def quit_dashboard(self):
        """Stop the dashboard"""
        self.dashboard.stop_live_mode()
        self.stop_listening()
    
    def refresh_data(self):
        """Force immediate data refresh"""
        if not self.paused:
            self.dashboard._update_all_panels()
    
    def show_help(self):
        """Display help overlay"""
        help_text = self.get_help_text()
        # Store help text to be displayed on next render
        self.dashboard._show_help = help_text
    
    def toggle_pause(self):
        """Toggle auto-refresh pause state"""
        self.paused = not self.paused
        status = "Paused" if self.paused else "Resumed"
        self.dashboard._status_message = f"Auto-refresh {status}"
    
    def cycle_theme(self):
        """Cycle through available themes"""
        themes = self.dashboard.theme_manager.get_available_themes()
        current_idx = themes.index(self.dashboard.theme)
        next_idx = (current_idx + 1) % len(themes)
        next_theme = themes[next_idx]
        
        self.dashboard.theme = next_theme
        self.dashboard.theme_manager.set_theme(next_theme)
        self.dashboard._status_message = f"Theme: {next_theme}"
    
    def increase_refresh_rate(self):
        """Increase refresh rate (faster updates)"""
        current = self.dashboard.refresh_rate
        new_rate = max(1, current - 1)
        self.dashboard.set_refresh_rate(new_rate)
        self.dashboard._status_message = f"Refresh rate: {new_rate}s"
    
    def decrease_refresh_rate(self):
        """Decrease refresh rate (slower updates)"""
        current = self.dashboard.refresh_rate
        new_rate = min(60, current + 1)
        self.dashboard.set_refresh_rate(new_rate)
        self.dashboard._status_message = f"Refresh rate: {new_rate}s"
    
    def export_config(self):
        """Export current configuration"""
        config = self.dashboard.export_layout()
        # Store config for export on next update
        self.dashboard._export_pending = config
        self.dashboard._status_message = "Configuration exported"
    
    def clear_screen(self):
        """Clear screen and force redraw"""
        self.dashboard.console.clear()
        self.dashboard._update_all_panels()
    
    def is_paused(self) -> bool:
        """Check if auto-refresh is paused"""
        return self.paused