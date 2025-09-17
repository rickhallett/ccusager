# 🚀 CCUsager - Intelligent Claude Code Usage Analytics

A sophisticated Python Rich CLI that transforms `bunx ccusage` into a powerful analytics and monitoring platform for Claude Code usage, providing real-time insights, cost optimization, and beautiful terminal visualizations.

## ✨ Features

### 🎯 Core Capabilities

- **Real-time Dashboard** - Live monitoring of Claude Code usage with auto-refreshing Rich panels
- **Smart Alerts** - Configurable budget thresholds with macOS notifications
- **Session Analysis** - Deep dive into conversation efficiency and token optimization
- **Beautiful Reports** - Export to PDF, HTML, CSV with charts and insights

### 🎨 Interactive Visualizations

```python
# Terminal-based real-time charts
ccusager dashboard --live
ccusager trends --chart=sparkline
ccusager heatmap --period=monthly
```

### 🔗 macOS Integration

- **Menu Bar Widget** - Ambient usage display via `rumps`
- **Spotlight Integration** - Quick usage queries
- **Notification Center** - Smart alerts for budget/usage milestones
- **Alfred Workflow** - Export ready workflow for power users
- **Raycast Extension** - Quick stats and session management

## 📦 Installation

```bash
# Via pip
pip install ccusager

# Via pipx (recommended)
pipx install ccusager

# Development
git clone https://github.com/yourusername/ccusager
cd ccusager
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Basic Usage

```bash
# Interactive dashboard
ccusager dashboard

# Quick stats
ccusager stats

# Budget monitoring
ccusager budget set 100 --period=daily
ccusager budget status

# Export reports
ccusager report --format=pdf --output=usage-report.pdf
```

### Advanced Pipelines

```bash
# Stream to system monitoring
bunx ccusage daily --json | ccusager stream --to=datadog

# Generate cost alerts
ccusager watch --threshold=50 | terminal-notifier -title "Claude Usage"

# Create usage heatmap
ccusager heatmap | imgcat  # iTerm2 inline images

# Session efficiency ranking
bunx ccusage session --json | ccusager analyze --metric=efficiency

# Export to spreadsheet with charts
ccusager export excel --with-charts --file=usage.xlsx

# Real-time cost ticker in tmux status
tmux set -g status-right '#(ccusager ticker --format=compact)'
```

## 🎮 Commands

### `dashboard`
Interactive Rich dashboard with panels for:
- Current session cost/tokens
- Daily/weekly/monthly trends  
- Model usage distribution
- Live burn rate indicator
- Context window utilization

```bash
ccusager dashboard [OPTIONS]

Options:
  --refresh INT     Refresh interval in seconds [default: 5]
  --theme TEXT      Color theme (monokai/dracula/nord) [default: monokai]
  --compact         Compact mode for smaller terminals
```

### `monitor`
Continuous monitoring with alerts:

```bash
ccusager monitor [OPTIONS]

Options:
  --budget FLOAT           Daily budget limit
  --alert-at INT          Alert at percentage of budget [default: 80]
  --sound                 Play sound on alerts
  --webhook URL           Send alerts to webhook
  --log FILE             Log usage to file
```

### `analyze`
Deep usage analytics:

```bash
ccusager analyze [COMMAND]

Commands:
  patterns        Identify usage patterns and habits
  efficiency      Score session token efficiency  
  forecast        Predict future usage and costs
  optimize        Suggest cost optimization strategies
  compare         Compare periods or projects
```

### `export`
Multi-format export capabilities:

```bash
ccusager export [FORMAT] [OPTIONS]

Formats:
  csv          Comma-separated values
  json         Structured JSON with metadata
  excel        XLSX with charts and formatting
  pdf          Professional PDF report
  html         Interactive HTML dashboard
  markdown     GitHub-flavored markdown

Options:
  --period TEXT       Period to export (daily/weekly/monthly)
  --include-charts    Add visualizations (excel/pdf/html)
  --template FILE     Custom Jinja2 template
```

### `stream`
Real-time data streaming:

```bash
ccusager stream [OPTIONS]

Options:
  --to SERVICE        Stream to service (datadog/grafana/prometheus)
  --format FORMAT     Output format (json/metrics/statsd)
  --buffer INT       Buffer size for batching [default: 10]
```

### `heatmap`
Generate usage heatmaps:

```bash
ccusager heatmap [OPTIONS]

Options:
  --period TEXT      Period (daily/weekly/monthly)
  --metric TEXT      Metric to visualize (cost/tokens/sessions)
  --output FILE      Save as image (PNG/SVG)
  --ascii            ASCII art output for terminals
```

### `predict`
ML-powered predictions:

```bash
ccusager predict [OPTIONS]

Options:
  --days INT         Days to forecast [default: 7]
  --confidence       Show confidence intervals
  --model TEXT       Prediction model (arima/prophet/lstm)
```

## 🔧 Configuration

### Config File (`~/.ccusager/config.yaml`)

```yaml
# Display preferences
theme: monokai
timezone: America/New_York
locale: en-US

# Budget settings
budgets:
  daily: 100.00
  weekly: 500.00
  monthly: 2000.00

# Alert configuration  
alerts:
  enabled: true
  channels:
    - terminal
    - notification
    - slack
  thresholds:
    warning: 0.7
    critical: 0.9

# Export defaults
export:
  default_format: excel
  include_charts: true
  template_dir: ~/.ccusager/templates

# Integration settings
integrations:
  datadog:
    api_key: ${DATADOG_API_KEY}
    tags:
      - env:production
      - team:engineering
  slack:
    webhook_url: ${SLACK_WEBHOOK_URL}

# Model preferences
models:
  track:
    - claude-sonnet-4
    - claude-opus-4
  optimization_target: cost  # or 'performance'
```

### Environment Variables

```bash
export CCUSAGER_CONFIG=~/.ccusager/config.yaml
export CCUSAGER_THEME=dracula
export CCUSAGER_CACHE_DIR=~/.ccusager/cache
export CCUSAGER_LOG_LEVEL=INFO
```

## 🎯 Use Cases

### 1. Team Usage Tracking

```bash
# Generate weekly team report
ccusager report team --period=weekly --format=pdf | \
  mail -s "Claude Usage Report" -a report.pdf team@company.com

# Slack integration for daily summaries
ccusager daily-summary | slack-cli post --channel="#eng-claude"
```

### 2. Cost Optimization Workflow

```bash
# Identify expensive patterns
ccusager analyze patterns --cost-focus | \
  ccusager optimize suggest > optimization-plan.md

# Monitor optimization impact
ccusager compare --before=20250901 --after=20250908 --metric=efficiency
```

### 3. Real-time Monitoring Stack

```bash
# Start monitoring stack
ccusager monitor --daemon &
ccusager stream --to=prometheus &
ccusager dashboard --server --port=8080 &

# View in browser
open http://localhost:8080
```

### 4. CI/CD Integration

```yaml
# .github/workflows/usage-check.yml
- name: Check Claude usage
  run: |
    ccusager check --max-daily=50 --exit-on-exceed
    ccusager report --format=markdown >> $GITHUB_STEP_SUMMARY
```

### 5. Personal Productivity

```bash
# Morning briefing
ccusager brief --yesterday | say

# Pomodoro integration  
ccusager session start --timer=25m --notify-on-complete

# End of day summary
ccusager summary --today --compare-average
```

## 🧪 Advanced Features

### Custom Analyzers

```python
# ~/.ccusager/plugins/custom_analyzer.py
from ccusager.analyzers import BaseAnalyzer

class CustomEfficiencyAnalyzer(BaseAnalyzer):
    def analyze(self, data):
        # Custom analysis logic
        return insights
```

### Webhook Handlers

```python
# Integrate with any service
ccusager webhook register \
  --url="https://api.company.com/claude-usage" \
  --events="budget_exceed,session_complete" \
  --auth="Bearer $API_TOKEN"
```

### Terminal Widgets

```bash
# tmux status line
set -g status-right '#(ccusager widget tmux)'

# Powerline segment
ccusager widget powerline --format=json

# iTerm2 status bar component
ccusager widget iterm2 --install
```

## 📊 Data Pipeline Examples

### Export to Data Warehouse

```bash
# BigQuery export
bunx ccusage daily --json | \
  ccusager transform --schema=bigquery | \
  bq load --source_format=NEWLINE_DELIMITED_JSON \
    project:dataset.claude_usage -

# Snowflake pipeline
ccusager export sql --dialect=snowflake | \
  snowsql -f - -o output_format=csv
```

### Grafana Dashboard

```bash
# Start Prometheus exporter
ccusager exporter prometheus --port=9090

# Import dashboard
ccusager dashboard export --format=grafana > claude-dashboard.json
```

### Jupyter Integration

```python
# In Jupyter notebook
from ccusager import UsageAnalyzer

analyzer = UsageAnalyzer()
df = analyzer.get_dataframe(period='monthly')
df.plot(x='date', y='cost', kind='bar')
```

## 🔐 Security & Privacy

- All data processed locally by default
- Optional encryption for cached data
- Secure credential storage via macOS Keychain
- No telemetry or external data sharing
- Audit log for all operations

## 🤝 Contributing

We love contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Development setup
git clone https://github.com/yourusername/ccusager
cd ccusager
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on the excellent `bunx ccusage` tool
- Powered by [Rich](https://github.com/Textualize/rich) for beautiful terminal UI
- Inspired by the Claude Code community

---

<p align="center">
  Made with ❤️ for the Claude Code community
</p>