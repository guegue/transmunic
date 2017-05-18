$(function() {
    $("#chart-bubble-1").click(function(){
        $(".chart-container [class*=' view-']").toggleClass( "view-main" )
        $("#ejecutado").toggleClass( "view-alternative" ).toggleClass( "view-main" )
    });
})
