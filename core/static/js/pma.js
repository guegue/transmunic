$(function() {
    $(".toggle-chart").click(function() {
        chartcontainer = $(this).data('chartcontainer');
        var charts = $("#" + chartcontainer).closest(".col-md-7").find(".view-main");
        $(charts).each(function(){
            $(this).hide("slow").removeClass("view-main").addClass("view-alternative");
        });

            $("#" + chartcontainer).show("slow", function(chartcontainer){
            var width = $( window ).width();
            var height = $( window ).height();
            console.log(width + "x" + height);
            if(!$(this).hasClass("bubbletree-wrapper")){
                if (width < 540){
                    $(this).highcharts().setSize(Math.round(width*0.8), width);
                }else if(width >= 540 && width < 720){
                    $(this).highcharts().setSize(432, 324);
                }else if(width >= 720 && width < 960){
                    $(this).highcharts().setSize(540, 405);
                }else if(width >= 960 && width < 1140){
                    $(this).highcharts().setSize(600, 450);
                }else{
                    $(this).highcharts().setSize(600, 450);
                }
            }
            $(this).removeClass("view-alternative").addClass("view-main");
        });

    });

    $("#show-detail-1").click(function() {
        $("#detail-1").toggle("slow");
    });

    $("#show-detail-2").click(function() {
        $("#detail-2").toggle("slow");
    });

    $("#show-detail-3").click(function() {
        $("#detail-3").toggle("slow");
    });
     $('body').on('submit', '#indicatorfilter', function (e) {
        e.preventDefault();
        let inputs_datos = $(this).serializeArray();
        let indicador = inputs_datos.find((obj) => {
            return (obj.name.toLowerCase() === 'indicador');
        });

         //NOTE: eliminando year de arreglo si indicador es transferencias
        if (indicador.value.includes('/transferencias')){
            inputs_datos = inputs_datos.filter((obj) => {
                return (obj.name.toLowerCase() !== 'year');
            });
        }

        //NOTE: eliminando indicador de arreglo
        inputs_datos = inputs_datos.filter((obj) => {
            return (obj.name !== indicador.name);
        });
        let url_indicador = indicador.value;
        //NOTE: crear parametros url
        let parameters = '?' + inputs_datos.map((parameter) => {
            if (parameter.value)
                return `${parameter.name}=${parameter.value}`;
        }, []).join('&');
        window.location.href = `${url_indicador}${parameters}`;
    });
});
