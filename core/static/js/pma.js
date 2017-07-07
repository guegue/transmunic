$(function() {
    $(".toggle-chart").click(function() {
        chartcontainer = $(this).data('chartcontainer');
        var charts = $("#" + chartcontainer).closest(".col-md-7").find(".view-main");
        $(charts).each(function(){
            $(this).hide("slow").removeClass("view-main").addClass("view-alternative");
        });
        console.log("is bubble " + !$("#" + chartcontainer).hasClass("bubbletree").toString(), chartcontainer);

            $("#" + chartcontainer).show("slow", function(){
            var width = $( window ).width();
                if(!$(this).hasClass("bubbletree")){
                if (width < 540){
                    $(this).highcharts().setSize(width, 320);
                }else if(width >= 540 && width < 720){
                    $(this).highcharts().setSize(400, 360);
                }else if(width >= 720 && width < 960){
                    $(this).highcharts().setSize(600, 400);
                    }else if(width >= 960 && width < 1140){
                    $(this).highcharts().setSize(600, 400);
                }else if(width > 1140){
                    $(this).highcharts().setSize(600, 400);
                }else {
                    $(this).highcharts().setSize(width);
                }
            }
            $(this).addClass("view-main");
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
