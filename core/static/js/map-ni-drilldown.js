$(function() {
    var data = Highcharts.geojson(Highcharts.maps['countries/ni/ni-all']),
        // Some responsiveness
        small = $('#nic-map-container').width() < 400;

    // Set drilldown pointers
    $.each(data, function(i) {
        this.drilldown = this.properties['hc-key'];
        this.value = i; // Non-random bogus data
    });
    $.each(ni_custom_data[0]['data'], function(i) {
        if (this.properties !== undefined) {
            this.drilldown = this.properties['hc-key'];
            this.name = this.properties['name'];
            this.dataLabels = {
                enabled: true,
                format: '{point.name}'
            };
            this.value = i; // Non-random bogus data
        }
    });

    // Instanciate the map
    Highcharts.mapChart('nic-map-container', {
        chart: {
            backgroundColor: "rgba(255,255,255,0)",
            events: {
                drilldown: function(e) {
                    if (!e.seriesOptions) {
                        var chart = this;
                        mapkey = '/static/maps/' + e.point.drilldown;
                        $.get(mapkey + '.json', function(data) {
                            $.each(data, function(i) {
                                this.value = i;
                            });
                            chart.showLoading('<i class="fa fa-refresh fa-spin fa-3x fa-fw"></i><span class="sr-only">Loading...</span>');
                            setTimeout(function() {
                                chart.hideLoading();
                                chart.addSeriesAsDrilldown(e.point, {
                                    name: e.point.name,
                                    data: data.data,
                                    dataLabels: {
                                        enabled: true,
                                        format: '{point.name}'
                                    },
                                    events: {
                                        click: function (e) {
                                            console.log(e.point);
                                            // location.href = 'https://en.wikipedia.org/wiki/' + e.point.name;
                                        }
                                    },
                                    allowPointSelect: false,
                                    states: {
                                        hover: {
                                            color: '#1891ac'
                                        }
                                    }
                                });
                            }, 1000);
                        });
                    }
                    this.setTitle('Rergesar a ', {
                        text: e.point.name
                    });
                },
                drillup: function() {
                    this.setTitle('Regresar a ', {
                        text: 'Nicaragua'
                    });
                }
            }
        },
        title: {
            text: ''
        },
        subtitle: {
            text: 'Nicaragua',
            floating: true,
            align: 'right',
            y: 50,
            style: {
                fontSize: '16px'
            }
        },
        legend: {
            enabled: false
        },
        mapNavigation: {
            enabled: true,
            buttonOptions: {
                verticalAlign: 'bottom'
            }
        },
        plotOptions: {
            map: {
                states: {
                    hover: {
                        color: '#1891ac'
                    }
                }
            }
        },
        series: ni_custom_data,
        drilldown: {
            activeDataLabelStyle: {
                color: '#FFFFFF',
                textDecoration: 'none',
                textOutline: '1px #000000'
            },
            drillUpButton: {
                relativeTo: 'spacingBox',
                position: {
                    x: 0,
                    y: 60
                }
            }
        }
    });
})
