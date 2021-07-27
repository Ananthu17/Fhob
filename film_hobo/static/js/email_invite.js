$(".enter-mail-id").keydown(function (e) {
    if (e.keyCode == 13 || e.keyCode == 32) {
      //alert('You Press enter');
       var getValue = $(this).val();
       $('.all-mail').append('<span class="email-ids">'+ getValue +' <span class="cancel-email">x</span></span>');
       $(this).val('');
    }
  });

  /// Cancel

  $(document).on('click','.cancel-email',function(){
            $(this).parent().remove();
        });

    // $('.enter-mail-id').click()