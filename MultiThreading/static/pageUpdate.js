/*
@author: Matteo Garbarino           --> ip address handling + some of the buttons
@author: Edoardo Calvi              --> the rest of the code
 */

var ip = "http://192.168.0.47:8080";
var score = 0;
var count = 0;

function hideInit(){
    //This function hides the "Taring . . . " part of the website after some seconds
    $("#init").hide();
}

function requestUpdates(){
    //This function makes HTTP GET requests to retrieve data, and update the page
    $.getJSON(ip+"/jsData/report",function (data) {
            var lh = data["history-last"];
            var lm = data["mic-last"];
            var sit = data["sit"];
            var desk = data["desk-last5"];
            var mic_th = data["mic-threshold"];

            var remainingSeconds = data["remainingTime"];
            var t_a_b = data["TAB"];
            var pausing = data["pausing"];
            score = data["score"];
            updateElements("web-time",lh);
            updateElements("last-mic",lm);
            updateElements("last-sit",sit);
            updateElements("load-cell5",desk);
            updateElements("mic-threshold",mic_th);
            updateElements("score",score);
            var b = $("#take-a-break");
            if (t_a_b === 1 || pausing === 1){
                if (t_a_b === 1){
                    b.text("You should definetely take a break.");
                }
                if (pausing===1){
                    var sec;
                    if (remainingSeconds < 0){
			sec = 0;
                        remainingSeconds = 0;
                    }
                    else{
                        sec = remainingSeconds % 60
                    }
                    remainingSeconds = remainingSeconds - sec;
                    var min = remainingSeconds / 60;
                    var st = "You still have ";
                    if (min < 10){
                        st = st + "0"
                    }
                    st = st + min + ":";
                    if (sec < 10){
                        st = st + "0";
                    }
                    st = st + sec + " minutes";
                    b.text(st);
                }
            }
            else{
                b.text("");
            }
    });
}

function updateElements(id,val){
    //This function changes the text of a certain html element with a given id
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

        /*
        //This part was written by Matteo Garbarino, it worked with pc tests but not on the raspberry.
        var y = document.getElementById("ip");
        var x = y.getAttribute("myIp");
        ip = ip+x+':8080';
        document.getElementById("ip").style.display = "none";
		*/

        $("#break-button").click(function () {
            $(".breaks").toggleClass("active");
        })
        $("#break-spend-button").click(function(){
            $(".distractions").toggleClass("active");
        })
        $("#break-study-button").click(function(){
            $(".breaks").toggleClass("active");
        })
        $("#score-button").click(requestUpdates);
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
        $("#plus-button").click(function() {
            count = count + 1;
            $("#counter").text(count);
        })
        $("#minus-button").click(function () {
            if (count>0){
                count = count - 1;
            }
            $("#counter").text(count);
        })
        $(".info-of-service button").click(function () {
            $(".time-amount").toggleClass("active");
            $("#minute-number").text(score/10);
        })
        $("#confirm").click(function () {
            if (count > 0){
                if (score/10 >= count){
                    $.get(
                        ip+"/functions/pausing/"+count,
                        function(data){
                            score = data["newscore"];
                            updateElements("score", score);
                        }
                    )
                    $(".time-amount").toggleClass("active");
                    $(".distractions").toggleClass("active");
                }
                else{
                    alert("You don't have enough points!");
                }
                count = 0;
                $("#counter").text(count);
            }

        })
        $("#break-nap-button").click(function () {
            $(".breaks").toggleClass("active");
            $.get(
                ip+"/functions/pausing/-1",
                function(data){
                    score = data["newscore"];
                    updateElements("score", score);
                }
            )
        })
        $("#break-coffee-button").click(function () {
            $(".breaks").toggleClass("active");
            $.get(
                ip+"/functions/coffee",
                function(data){
                    score = data["newscore"];
                    updateElements("score", score);
                }
            )
        })


    }
);