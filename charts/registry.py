from charts.nps_default_renderer import NPSBarChartDefaultRenderer
from charts.nps_renderer import NPSBarChartRenderer
from charts.csat_renderer import CSATBarChartRenderer
from charts.percentage_stacked_bar_chart_render import PercentageStackedBarChartRenderer

CHART_RENDERER_REGISTRY = {
    "NPSBarChartWidget" : NPSBarChartRenderer,
    "NPSBarChartDefaultWidget" : NPSBarChartDefaultRenderer,
    "CSATBarChartWidget" : CSATBarChartRenderer,
    "PercentageStackedBarChartWidget" : PercentageStackedBarChartRenderer
}

def create_renderer(data, config, group_by):
    cls = CHART_RENDERER_REGISTRY.get(config.get('type'))

    if not cls:
        raise ValueError(f"Unknown chart type: {config.get('type')}")
    
    return cls(data, config, group_by)