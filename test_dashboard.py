#!/usr/bin/env python
"""Quick test script to verify dashboard functionality"""

import time
from ccusager.modules.dashboard import RichDashboardModule
from ccusager.interfaces import DashboardPanel

def test_dashboard():
    """Test the dashboard with mock data"""
    print("Creating dashboard...")
    dashboard = RichDashboardModule()
    
    # Add test panels
    panels = [
        DashboardPanel(
            id="cost",
            title="Total Cost",
            type="metric",
            position=(0, 0),
            size=(1, 1),
            data={},
            refresh_rate=5
        ),
        DashboardPanel(
            id="model_dist",
            title="Model Distribution",
            type="distribution",
            position=(1, 0),
            size=(1, 2),
            data={},
            refresh_rate=10
        )
    ]
    
    config = {
        "theme": "monokai",
        "refresh_rate": 5,
        "default_panels": [
            {
                "id": p.id,
                "title": p.title,
                "type": p.type,
                "position": p.position,
                "size": p.size,
                "data": p.data,
                "refresh_rate": p.refresh_rate
            }
            for p in panels
        ]
    }
    
    print("Initializing dashboard...")
    dashboard.initialize(config)
    
    print("Dashboard initialized successfully!")
    print("Testing data source (mock mode)...")
    
    data = dashboard.data_source.fetch_current_data()
    print(f"  Total Cost: ${data.get('total_cost', 0):.2f}")
    print(f"  Total Tokens: {data.get('total_tokens', 0):,}")
    print(f"  Burn Rate: ${data.get('burn_rate', 0):.4f}/hr")
    
    print("\nDashboard test complete! Use 'ccusager dashboard' to launch interactive mode.")

if __name__ == "__main__":
    test_dashboard()