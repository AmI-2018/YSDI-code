function hideInit(){
    $("#init").hide();
}

function requestUpdates(){
    $.getJSON("http://192.168.1.66:8080/jsData/tare",function (data) {
            var diz = data["values"];
            var val = diz["mic"];
            updateElements("mic-tare",val);
    });
    $.getJSON("http://192.168.1.66:8080/jsData/visits",function (data) {
            var hc = data["history-count"];
            var mc = data["mic-count"];
            updateElements("sites-number",hc);
            updateElements("speak-number",mc);
    });
}

function updateElements(id,val){
    $("#"+id).text(val);
}

function tare(){
    $("#init").show();
    setTimeout(function(){
            $("#init").hide()
        },3000);
    $.getJSON("http://192.168.1.66:8080/constants/tare");
}

$(document).ready(function() {
        var v = setTimeout(hideInit,4000);
        $("#tare-button").click(tare);
        setInterval(requestUpdates,5000);
    }
);