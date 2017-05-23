$(function() {
    $("#chart-pie-1").click(function(){
        $(".chart-container .view-main").hide("slow");
        $(".chart-container .view-main").removeClass("view-main").addClass("view-alternative"); 
        $("#ejecutado").show("slow").addClass("view-main");
    });
    $("#chart-bubble-1").click(function(){
        $(".chart-container .view-main").hide("slow");
        $(".chart-container .view-main").removeClass("view-main").addClass("view-alternative"); 
        $("#bubble-1").show("slow").addClass("view-main");
    });
    $("#chart-bar-1").click(function(){
        $(".chart-container .view-main").hide("slow");
        $(".chart-container .view-main").removeClass("view-main").addClass("view-alternative"); 
        $("#ejecutado_column").show("slow").addClass("view-main");
    });
});
