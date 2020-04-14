from django.conf import settings

from chartit import Chart, RawDataPool

colorscheme = settings.CHARTS_COLORSCHEME
colors_array = settings.COLORS_ARRAY
chart_options = settings.CHART_OPTIONS


def graphChart(parameters):
    data_bar = RawDataPool(
        series=[
            {
                'options': {
                    'source': parameters.get('data')
                },
                'terms': [
                    parameters.get('field1'),
                    parameters.get('field2'),
                ]
            }
        ]
    )
    bar_chart = Chart(
        datasource=data_bar,
        series_options=[
            {
                'options': {
                    'type': parameters.get('typechart'),
                    'colorByPoint': True,
                },
                'terms': {
                    parameters.get('field1'): [
                        parameters.get('field2')
                    ]
                },
            }],
        chart_options={
            'legend': {
                'enabled': False
            },
            'colors': colors_array,
            'title': {
                'text': parameters.get('title')
            },
            'xAxis': {
                'title': {
                    'text': parameters.get('labelX_axis')
                }
            },
            'yAxis': {
                'title': {
                    'text': parameters.get('labelY_axis')
                }
            },
            'tooltip': {
                'pointFormat': parameters.get('pointFormat'),
            }
        },
        x_sortf_mapf_mts=(None, None, False, True),
    )

    return bar_chart


def graphTwoBarChart(parameters):
    data_bar = RawDataPool(
        series=[
            {
                'options': {
                    'source': parameters.get('data')
                },
                'terms': [
                    parameters.get('field1'),
                    parameters.get('field2'),
                    parameters.get('field3'),
                ]
            }
        ]
    )
    bar_chart = Chart(
        datasource=data_bar,
        series_options=[
            {
                'options': {
                    'type': 'column',
                    'colorByPoint': True,
                },
                'terms': {
                    parameters.get('field1'): [
                        parameters.get('field2'),
                        parameters.get('field3'),
                    ]
                },
            }],
        chart_options={
            'legend': {
                'enabled': False
            },
            'colors': colors_array,
            'title': {
                'text': parameters.get('title')
            },
            'xAxis': {
                'title': {
                    'text': parameters.get('labelX_axis')
                }
            },
            'yAxis': {
                'title': {
                    'text': parameters.get('labelY_axis')
                }
            }
        })

    return bar_chart
