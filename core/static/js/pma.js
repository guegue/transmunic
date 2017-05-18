$(function() {
    $("#chart-pie-1").click(function(){
        $(".chart-container [class*=' view-']").toggleClass( "view-main" )
        $("#bubble-1").hide("slow");
        $("#ejecutado").show("slow");
    });
    $("#chart-bubble-1").click(function(){
        $(".chart-container [class*=' view-']").toggleClass( "view-main" )
        $("#ejecutado").hide("slow");
        $("#bubble-1").show("slow");
    });
});