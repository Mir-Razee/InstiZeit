$(document).ready(function () {
    var socket = io();
    $.ajax({
        type: 'GET',
        url: '/msg/getgrps',
        success: function (data) {
            obj = JSON.parse(data);
            for (var i = 0; i < obj.length; i++) {
                $('#grp-container').append('<div class="grp_box">' + obj[i] + '</div>');
            }
        }
    });
    $.ajax({
        type: 'GET',
        url: '/msg/getfrnds',
        success: function (data) {
            obj = JSON.parse(data);
            for (var i = 0; i < obj.length; i++) {
                $('#frnd-container').append('<div class="frnd_box">' + obj[i] + '</div>');
            }
        }
    });

    socket.on('my response', function (msg) {
        if (msg.data) {
            $('#msg-container').append('<p class="from-them">' + msg.data + '</p>');
        }
        scrollBottom();
    });
    socket.on('initial connect', function (msg) {
        var msg = JSON.parse(msg);
        for (var i = 0; i < msg.length; i++) {
            $('#msg-container').append('<p class="from-them">' + msg[i][1] + ':<br>' + msg[i][2] + '</p>');
        }
        scrollBottom();
    });
    $('form#msg').submit(function (event) {
        if ($('#textbox').val()) {
            $('#msg-container').append('<p class="from-me">' + $('#textbox').val() + '</p>');
            socket.emit('my event', { data: $('#textbox').val() });
            $('#textbox').val('');
        }
        scrollBottom();
        return false;
    });
    $('form#broadcast').submit(function (event) {
        socket.emit('my broadcast event', { data: $('#broadcast_data').val() });
        return false;
    });

    $(document).on('click','#get-msgs',function(){
        var grp=this.value;
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
                for (var i = 0; i < obj.length; i++) {
                    $('#msg-container').append('<p class="from-them">' + obj[i][1] + ':<br>' + obj[i][2] + '</p>');
                    scrollBottom();
                }
            }
        });
    })

});

var scrollBottom=function(){
    $('#msg-container').scrollTop($('#msg-container')[0].scrollHeight);
}