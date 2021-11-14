

$(document).ready(function () {
  $(document).on('click','#likebtn',function(){
        postid = this.value;

        $.ajax({
            type: 'GET',
            url: '/likes',
            data: {postid:postid},
            success: function (data) {
                $( "#post" ).load(window.location.href + "#post" );
            }
        });
    })
});