var ratingValue = ""
origin_url = window.location.origin
feedback_url = origin_url + '/hobo_user/feedback-api/'

email_element = $("[id=id_email]")
name_element = $("[id=id_name]")
user_feedback_element = $("[id=id_user_feedback]")

$(document).ready(function(){
    $('#stars li').on('mouseover', function(){
      var onStar = parseInt($(this).data('value'), 10);
      $(this).parent().children('li.star').each(function(e){
        if (e < onStar) {
          $(this).addClass('hover');
        }
        else {
          $(this).removeClass('hover');
        }
      });

    }).on('mouseout', function(){
      $(this).parent().children('li.star').each(function(e){
        $(this).removeClass('hover');
      });
    });

    $('#stars li').on('click', function(){
      var onStar = parseInt($(this).data('value'), 10);
      var stars = $(this).parent().children('li.star');

      for (i = 0; i < stars.length; i++) {
        $(stars[i]).removeClass('selected');
      }

      for (i = 0; i < onStar; i++) {
        $(stars[i]).addClass('selected');
      }
      var ratingValue = parseInt($('#stars li.selected').last().data('value'), 10);
    });

    $('#feedback-submit').click(function(event){
      event.preventDefault();

      var ratingValue = parseInt($('#stars li.selected').last().data('value'), 10);
      if (isNaN(ratingValue)){
        ratingValue = ""
      }

      feedback_url_args = {
        "email": email_element.val(),
        "name": name_element.val(),
        "user_rating": ratingValue,
        "user_feedback": user_feedback_element.val()
      }

      axios.post(feedback_url, feedback_url_args)
      .then((response) => {
          console.log(response);
      }, (error) => {
        console.log(error.response.data.user_feedback);
        if (error.response.data.user_rating){
          $('#error-star').html(error.response.data.user_rating);
        }
        else{
          $('#error-star').empty()
        }

        if (error.response.data.email){
          $('#error-email').html(error.response.data.email);
        }
        else{
          $('#error-email').html('');
        }

        if (error.response.data.name){
          $('#error-name').html(error.response.data.name);
        }
        else{
          $('#error-name').html('');
        }

        if (error.response.data.user_feedback){
          $('#error-feedback').html(error.response.data.user_feedback);
        }
        else{
          $('#error-feedback').html('');
        }

      });

    });


});



