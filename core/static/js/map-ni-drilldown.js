$(function () {
    var data = Highcharts.geojson(Highcharts.maps['countries/ni/ni-all']),
        // Some responsiveness
        small = $('#nic-map-container').width() < 400;

    // Set drilldown pointers
    $.each(data, function (i) {
        this.drilldown = this.properties['hc-key'];
        this.value = i; // Non-random bogus data
    });
    $.each(ni_custom_data[0]['data'], function (i) {
        if (this.properties !== undefined) {
            this.drilldown = this.properties['hc-key'];
            this.name = this.properties['name'];
            this.dataLabels = {
                enabled: true,
                format: '{point.name}'
            };
            this.animation = false;
            // this.value = i; // Non-random bogus data
        }
    });

    // Instanciate the map
    Highcharts.mapChart('nic-map-container', {
        chart: {
            backgroundColor: "rgba(255,255,255,0)",
            style: {
                fontFamily: '"Raleway",sans-serif'
            },
            events: {
                drilldown: function (e) {
                    if (!e.seriesOptions) {
                        var chart = this;
                        mapkey = '/static/maps/' + e.point.drilldown;
                        $.get(mapkey + '.json', function (data) {
                            $.each(data, function (i) {
                                this.value = i;
                                this.cursor = 'pointer';
                            });
                            chart.showLoading('<i class="fa fa-refresh fa-spin fa-3x fa-fw"></i><span class="sr-only">Loading...</span>');
                            setTimeout(function () {
                                chart.hideLoading();
                                chart.addSeriesAsDrilldown(e.point, {
                                    name: e.point.name,
                                    data: data.data,
                                    dataLabels: {
                                        enabled: true,
                                        allowOverlap: true,
                                        crop: false,
                                        overflow: 'none',
                                        format: '{point.name}'
                                    },
                                    tooltip: {
                                        headerFormat: '<small>{series.name}</small>',
                                        pointFormat: '<br><span>{point.name}</span>'
                                    },
                                    events: {
                                        click: function (e) {
                                            location.href = '/municipio/' + e.point.slug;
                                        }
                                    },
                                    states: {
                                        hover: {
                                            color: '#2b7ab3'
                                        }
                                    },
                                    cursor: 'pointer'
                                });
                            }, 1000);
                        });
                    }
                    this.setTitle('Regresar a ', {
                        text: e.point.name
                    });
                },
                drillup: function () {
                    this.setTitle('Regresar a ', {
                        text: 'Nicaragua'
                    });
                }
            }
        },
        tooltip: {
            headerFormat: '',
            pointFormat: '<span>{point.name}</span>'
        },
        title: {
            text: '<b>Presupuesto</b> Municipal',
            floating: false,
            align: 'left',
            style: {
                color: '#ffffff',
                fontSize: '18px'
            }
        },
        subtitle: {
            text: 'Haga click en su municipio para<br/> revisar el presuspuesto',
            floating: true,
            align: 'left',
            y: 50,
            style: {
                color: '#ffffff',
                fontSize: '14px'
            }
        },
        legend: {
            enabled: false
        },
        mapNavigation: {
            enabled: true,
            buttonOptions: {
                align: 'right',
                verticalAlign: 'bottom'
            }
        },
        plotOptions: {
            map: {
                states: {
                    hover: {
                        color: '#2b7ab3'
                    }
                }
            },
            series: {
                dataLabels: {
                    enabled: true,
                    allowOverlap: true,
                    overflow: 'none',
                    cursor: 'pointer'
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
        },
        lang: {
            contextButtonTitle: "Menú contextual del gráfico",
            decimalPoint: ".",
            downloadJPEG: "Descargar imágen JPEG",
            downloadPDF: "Descargar documento PDF",
            downloadPNG: "Descargar imágen PNG",
            downloadSVG: "Descargar SVG",
            drillUpText: "↩ Regresar",
            loading: "Cargando...",
            months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            noData: "No hay datos que mostrar",
            numericSymbolMagnitude: 1000,
            numericSymbols: ["k", "M", "G", "T", "P", "E"],
            printChart: "Imprimir gráfico",
            resetZoom: "Restablecer zoom",
            resetZoomTitle: "Restablecer nivel de zoom 1:1",
            shortMonths: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            thousandsSep: " ",
            weekdays: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        }
    });
})
