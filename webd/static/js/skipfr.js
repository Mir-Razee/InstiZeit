$(document).ready(function () {
  $.ajax({
          type: 'GET',
          url: '/getdata',
          success:function(data){
          data=JSON.parse(data);

        for(var i=0;i<data.length;i=i+2)
         {
              $('#fr-container').append(`
              <img src="${data[i+1]}" class="w3-circle" alt="Avatar" style="width:50%"><br>
              <span>${data[i]}</span>
              <div class="w3-row w3-opacity">
                <div class="w3-half">
                  <button class="w3-button w3-block w3-green w3-section" title="Accept" type="submit" value="1" name="Res"><i class="fa fa-check"></i></button>
                </div>
                <div class="w3-half">
                  <button class="w3-button w3-block w3-red w3-section" title="Decline" type="submit" value="0" name="Res"><i class="fa fa-remove"></i></button>
                </div>
              </div>
             `)
           }
           if(data.length==0){
           $('#fr-container').append(`<p>NONE</p>`)
          }
          }
        });
});