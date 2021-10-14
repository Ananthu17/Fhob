
origin_url = window.location.origin
report_url = origin_url + '/hobo_user/report-a-problem-api/'


email_element = $("[id=id_email]")
name_element = $("[id=id_name]")
phone_element = $("[id=id_phone]")
user_report_element = $("[id=id_comment]")

 $(document).ready(function(){


    $('#mem-close-btn').click(function(event){
      location.reload();
    });

    $('#report').click(function(event){
      event.preventDefault();

      

      $(function () {
        $('#noti-modal').on('click', function () {
            $('#notificationModal').modal('hide');
          
           
        })
      })
      $(function () {
        $('#mem-close-btn').on('click', function () {
            $('#notificationModal').modal('hide');
           
        })
      })
    

      report_url_args = {
        "user_email": email_element.val(),
        "name": name_element.val(),
        "user_phone" : phone_element.val(),
        "user_problem": user_report_element.val()
      }

      axios.post(report_url, report_url_args)
      .then((response) => {
          var modal = $("#notificationModal")
          var modal_text = "Thanks for Your Response"
          var title = "Report a Problem"
          modal.find('.modal-title').text(title)
          modal.find('.modal-body').text(modal_text)
          $("#notificationModal").modal('show');
         
      
        }, (error) => {
        console.log(error.response.data.user_problem);

        if (error.response.data.user_email){
          $('#error-email').html(error.response.data.user_email);
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
        if (error.response.data.user_phone){
          $('#error-phone').html(error.response.data.user_phone);
        }
        else{
          $('#error-phone').html('');
        }
        if (error.response.data.user_problem){
          $('#error-problem').html(error.response.data.user_problem);
        }
        else{
          $('#error-problem').html('');
        }

      });



    });

  
 });



