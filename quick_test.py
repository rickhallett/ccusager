#!/usr/bin/env python
"""Quick test to see the dashboard in live mode for a few seconds"""

import time
import threading
from ccusager.modules.dashboard import RichDashboardModule

def test_live_dashboard():
    """Test dashboard in live mode for 5 seconds"""
    dashboard = RichDashboardModule()
    
    # Initialize with simple config
    config = {
        "theme": "monokai",
        "refresh_rate": 2,
        "default_panels": []
    }
    dashboard.initialize(config)
    
    print("Starting dashboard for 5 seconds... Press Ctrl+C to exit early")
    
    # Start live mode in a thread and stop it after 5 seconds
    def stop_after_delay():
        time.sleep(5)
        dashboard.stop_live_mode()
    
    stop_thread = threading.Thread(target=stop_after_delay, daemon=True)
    stop_thread.start()
    
    try:
        dashboard.start_live_mode()
    except KeyboardInterrupt:
        dashboard.stop_live_mode()
    
    print("\nDashboard test complete!")

if __name__ == "__main__":
    test_live_dashboard()