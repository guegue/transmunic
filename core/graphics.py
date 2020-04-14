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
                },
                'tickInterval': 100
            },
            'tooltip': {
                'pointFormat': parameters.get('pointFormat'),
            }
        },
        x_sortf_mapf_mts=(None, None, False, True),
    )

    return bar_chart


def graphPie(parameters):
    data_pie = RawDataPool(
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
    pie_chart = Chart(
        datasource=data_pie,
        series_options=[
            {
                'options': {
                    'type': 'pie',
                    'stacking': False,
                },
                'terms': {
                    parameters.get('field1'): [
                        parameters.get('field2')
                    ]
                },
            }],
        chart_options={
            'credits': {
                'enabled': False
            },
            'legend': {
                'enabled': True
            },
            'title': {
                'enabled': False,
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
            'colors': colors_array,
            'tooltip': {
                'pointFormat': parameters.get('pointFormat'),
            },
            'plotOptions': {
                'column': {
                    'depth': 35,
                    'showInLegend': False,
                    'dataLabels': {
                        'enabled': False,
                        'format': parameters.get('format').replace('percentage', 'y', 1)
                    }
                },
                'pie': {
                    'depth': 35,
                    'showInLegend': True,
                    'dataLabels': {
                        'enabled': True,
                        'format': parameters.get('format')
                    }
                }
            }
        },
        x_sortf_mapf_mts=(None, None, False, True),
    )

    return pie_chart


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
