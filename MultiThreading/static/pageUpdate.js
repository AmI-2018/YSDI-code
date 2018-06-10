var ip = "http://";

function hideInit(){
    $("#init").hide();
}

function requestUpdates(){
    $.getJSON(ip+"/jsData/tare",function (data) {
            var diz = data["values"];
            var val = diz["mic"];
            updateElements("mic-tare",val);
    });
    $.getJSON(ip+"/jsData/visits",function (data) {
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
    $.getJSON(ip+"/constants/tare");
}

function score(){
    $("#init").show();
    setTimeout(function(){
            $("#init").hide()
        },3000);
    $.getJSON(ip+"/constants/tare");
}

$(document).ready(function() {
        var v = setTimeout(hideInit,4000);
        $("#tare-button").click(tare);
        setInterval(requestUpdates,5000);

        var y = document.getElementById("ip");
        var x = y.getAttribute("myIp");
        ip = ip+x+':8080';
        document.getElementById("ip").style.display = "none";

        $("#break-button").click(function () {
            $(".breaks").toggleClass("active");
        })
        $("#break-spend-button").click(function(){
            $(".distractions").toggleClass("active");
        })
        $("#break-study-button").click(function(){
            $(".breaks").toggleClass("active");
        })
        $("#score-button").click(function () {
            $.getJSON(ip+"/functions/updateScore", function (data) {
                val = data["newScore"];
                updateElements("score",val);
            })
        })
        $("#repeating-button").click(function () {
            $.getJSON(ip+"/functions/repeating", function (data){
                val = data["newScore"];
                updateElements("score",val);
            })
        })
        $("#stop-button").click(function () {
            $.get(ip + "/functions/stopStudying", function (data) {
                $("body").html(data);
            })
        })
        $("#score").click(function () {
            $(".debug").toggleClass("active");
        })

    }
);