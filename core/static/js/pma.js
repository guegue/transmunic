$(function() {
    $(".toggle-chart").click(function() {
        $(this).closest(".col-md-7").find(".chart-container .view-main").hide("slow");
        $(this).closest(".col-md-7").find(".chart-container .view-main").addClass("view-alternative");
        chartcontainer = $(this).data('chartcontainer');
        $("#" + chartcontainer).show("slow").addClass("view-main");
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
