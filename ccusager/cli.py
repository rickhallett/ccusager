"""Command-line interface for CCUsager"""

import click
import yaml
import json
from pathlib import Path
from typing import Optional

from .modules.dashboard import RichDashboardModule
from .interfaces import DashboardPanel


@click.group()
@click.version_option(version="0.1.0")
def main():
    """CCUsager - Intelligent Claude Code Usage Analytics"""
    pass


@main.command()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--theme', '-t', type=click.Choice(['monokai', 'dracula', 'nord']), default='monokai', help='Dashboard theme')
@click.option('--refresh', '-r', type=int, default=5, help='Refresh rate in seconds')
@click.option('--compact', is_flag=True, help='Use compact mode for smaller terminals')
def dashboard(config: Optional[str], theme: str, refresh: int, compact: bool):
    """Launch the real-time dashboard"""
    
    # Load configuration if provided
    dashboard_config = {
        "theme": theme,
        "refresh_rate": refresh,
        "compact_mode": compact
    }
    
    if config:
        config_path = Path(config)
        if config_path.suffix == '.yaml' or config_path.suffix == '.yml':
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                dashboard_config.update(user_config)
        elif config_path.suffix == '.json':
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                dashboard_config.update(user_config)
    
    # Create and initialize dashboard
    dashboard_module = RichDashboardModule()
    
    # Set up default panels for Phase 2
    default_panels = [
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
            id="tokens",
            title="Total Tokens",
            type="metric",
            position=(0, 1),
            size=(1, 1),
            data={},
            refresh_rate=5
        ),
        DashboardPanel(
            id="burn_rate",
            title="Burn Rate",
            type="metric",
            position=(1, 0),
            size=(1, 1),
            data={},
            refresh_rate=5
        ),
        DashboardPanel(
            id="efficiency",
            title="Efficiency Score",
            type="metric",
            position=(1, 1),
            size=(1, 1),
            data={},
            refresh_rate=5
        ),
        DashboardPanel(
            id="model_dist",
            title="Model Distribution",
            type="distribution",
            position=(2, 0),
            size=(1, 2),
            data={},
            refresh_rate=10
        ),
        DashboardPanel(
            id="context_util",
            title="Context Utilization",
            type="gauge",
            position=(3, 0),
            size=(1, 1),
            data={},
            refresh_rate=5
        ),
        DashboardPanel(
            id="trend",
            title="Cost Trend (24h)",
            type="chart",
            position=(3, 1),
            size=(1, 1),
            data={},
            refresh_rate=10
        )
    ]
    
    dashboard_config["default_panels"] = [
        {
            "id": panel.id,
            "title": panel.title,
            "type": panel.type,
            "position": panel.position,
            "size": panel.size,
            "data": panel.data,
            "refresh_rate": panel.refresh_rate
        }
        for panel in default_panels
    ]
    
    # Initialize dashboard with configuration
    dashboard_module.initialize(dashboard_config)
    
    # Start live mode
    try:
        click.echo("Starting CCUsager Dashboard... Press Ctrl+C to exit.")
        dashboard_module.start_live_mode()
    except KeyboardInterrupt:
        dashboard_module.stop_live_mode()
        click.echo("\nDashboard stopped.")


@main.command()
def stats():
    """Show quick usage statistics"""
    # Placeholder for stats command
    from .modules.dashboard.data_source import CCUsageDataSource
    
    data_source = CCUsageDataSource()
    data = data_source.fetch_current_data()
    
    click.echo("Claude Code Usage Statistics")
    click.echo("=" * 40)
    click.echo(f"Total Cost: ${data.get('total_cost', 0):.2f}")
    click.echo(f"Total Tokens: {data.get('total_tokens', 0):,}")
    click.echo(f"Burn Rate: ${data.get('burn_rate', 0):.4f}/hr")
    
    model_dist = data.get('model_distribution', {})
    if model_dist:
        click.echo("\nModel Distribution:")
        for model, percentage in model_dist.items():
            click.echo(f"  {model}: {percentage:.1f}%")


@main.command()
@click.option('--format', '-f', type=click.Choice(['yaml', 'json']), default='yaml', help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def export_config(format: str, output: Optional[str]):
    """Export dashboard configuration"""
    dashboard = RichDashboardModule()
    config = dashboard.export_layout()
    
    if format == 'yaml':
        output_text = yaml.dump(config, default_flow_style=False)
    else:
        output_text = json.dumps(config, indent=2)
    
    if output:
        with open(output, 'w') as f:
            f.write(output_text)
        click.echo(f"Configuration exported to {output}")
    else:
        click.echo(output_text)


if __name__ == "__main__":
    main()