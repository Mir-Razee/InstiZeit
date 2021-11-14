$(document).ready(function () {
    var socket = io();

    $.ajax({
        type: 'GET',
        url: '/msg/getgrps',
        success: function (data) {
            obj = JSON.parse(data);
            for (var i = 0; i < obj.length; i++) {
                if(obj[i][1].slice(0,6)=="friend"){
                    $('#frnd-container').append(`<div class="grp_box"> <button id="get-msgs" value=${obj[i][0]}  class="btn btn-primary">`+ obj[i][1].slice(6)+ '</button> </div>');
                }
                else{
                    $('#grp-container').append(`<div class="grp_box"> <button id="get-msgs" value="${obj[i][0]}" class="btn btn-primary">` + obj[i][1].slice(5) + '</button> </div>');
                }
            }
        }
    });

    socket.on('my response', function (msg) {
        var msg = JSON.parse(msg);
        for (var i = 0; i < msg.length; i+=2) {
            $('#msg-container').append('<p class="from-them">' + msg[i+1] + ':<br>' + msg[i][2] + '</p>');
        }
        scrollBottom();
    });

    socket.on('initial connect', function (msg) {
        var msg = JSON.parse(msg);
        for (var i = 0; i < msg.length; i+=2) {
            $('#msg-container').append('<p class="from-them">' + msg[i+1] + ':<br>' + msg[i][2] + '</p>');
        }
        scrollBottom();
    });

    $('form#msg').submit(function (event) {
        if ($('#textbox').val()) {
            var today = new Date();
            var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
            var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
            socket.emit('my event', { message: $('#textbox').val(), grp:$("#grp_identifier").val(),date:date,time:time});
            $('#textbox').val('');
            $('#textbox').focus();
        }
        scrollBottom();
        return false;
    });

    $(document).on('click','#get-msgs',function(){
        socket.emit('leave_room',{
            room: $("#grp_identifier").val()
        });
        
        var grp=this.value;
        $("#grp_identifier").attr("value",`${grp}`);
        
        socket.emit('join_room',{
            room:`${grp}`
        });

        $.ajax({
            type: 'GET',
            url: '/msg/get_msgs',
            data: {id:grp},
            success: function (data) {
                obj = JSON.parse(data);
                var cont=document.getElementById("msg-container");
                while(cont.firstChild){
                    cont.removeChild(cont.firstChild);
                }
                for (var i = 0; i < obj.length; i+=2) {
                    $('#msg-container').append('<p class="from-them">' + obj[i+1] + ':<br>' + obj[i][2] + '</p>');
                    scrollBottom();
                }
            }
        });
    })

});

var scrollBottom=function(){
    $('#msg-container').scrollTop($('#msg-container')[0].scrollHeight);
}