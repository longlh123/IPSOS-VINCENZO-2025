from charts.nps_default_renderer import NPSBarChartDefaultRenderer
from charts.nps_renderer import NPSBarChartRenderer
from charts.csat_renderer import CSATBarChartRenderer

CHART_RENDERER_REGISTRY = {
    "NPSBarChartWidget" : NPSBarChartRenderer,
    "NPSBarChartDefaultWidget" : NPSBarChartDefaultRenderer,
    "CSATBarChartWidget" : CSATBarChartRenderer
}

def create_renderer(data, config, group_by):
    cls = CHART_RENDERER_REGISTRY.get(config.get('type'))

    if not cls:
        raise ValueError(f"Unknown chart type: {config.get('type')}")
    
    return cls(data, config, group_by)