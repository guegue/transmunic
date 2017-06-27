$(function() {
    $(".toggle-chart").click(function(){
        $(this).closest(".col-md-7").find(".chart-container .view-main").hide("slow");
        $(this).closest(".col-md-7").find(".chart-container .view-main").addClass("view-alternative");
        chartcontainer = $(this).data('chartcontainer');
        $("#"+chartcontainer).show("slow").addClass("view-main");
    });

    $("#show-detail-1").click(function(){
        $("#detail-1").toggle("slow");
    });

    $("#show-detail-2").click(function(){
        $("#detail-2").toggle("slow");
    });

    $("#show-detail-3").click(function(){
        $("#detail-3").toggle("slow");
    });
    $('#indicatorfilter').submit(function(){
      var indicator = $("#indicator option").filter(":selected").val();
      var year = $("#year option").filter(":selected").val();
      var municipio = $('.municipio').select2('data')[0].id;

      if( indicator == "" && (municipio !== "Consolidado Municipal") && (municipio !="")){
          location.href = '/'+ municipio ;
      }
      else if( indicator !== "" ){
          location.href = '/core/'+ indicator + '?' + 'municipio=' + municipio + '&' + 'year=' + year + '&' + 'indicador=' + indicator;
      }
      else {
          location.href = '/';
      }
      return false;
    });
});
