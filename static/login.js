$(document).ready(function() {
    $(document).on('keypress', function(event) {
        let keycode = (event.keyCode ? event.keyCode : event.which);
          if(keycode == '13') {
            console.log('You pressed a "enter" key');
            $('form[action|="/login"]')[0].submit();
          }
    })
});