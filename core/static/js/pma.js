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
                    $(this).highcharts().setSize(width, width);
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
    $('#indicatorfilter').submit(function() {
        var indicator = $("#indicator option").filter(":selected").val();
        var year = $("#year option").filter(":selected").val();
        var municipio = $('.municipio').select2('data')[0].id;
        var path = "/";
        var qs = 'year=' + year;
        if (indicator == "resumen-municipal" && municipio != ""){
            path = "/" + municipio;
        } else if (indicator == "resumen-municipal" && municipio == "") {
            path = "/resumen-municipal/";
        } else if (indicator != "resumen-municipal") {
            path = '/core/' + indicator;
            qs += '&indicador=' + indicator;
            if(municipio !=""){
                qs += '&municipio=' + municipio;
            }
        }
        if(qs != ""){
            qs = "?" + qs;
        }
        location.href = path + qs;
        return false;
    });
});
