
    $.fn.stars = function() {
        return this.each(function() {
          // Get the value
          var val = parseFloat($(this).html());
          // Make sure that the value is in 0 - 5 range, multiply to get width
          var size = Math.max(0, (Math.min(5, val))) * 36.5;
          // Create stars holder
          var $span = $('<span> </span>').width(size);
          // Replace the numerical value with stars
          $(this).empty().append($span);
        });
      }

      $(function() {
        $('.results-content span.stars').stars();
      });

      $(".rate").change(function(){
          var rate = $(this).val();
          var id = $(this).attr('id');
          var job = id.split("-")[1];
          var div_id = "#reason-div-"+job;
          var form_id = "#rating-form-"+job;
          console.log(form_id)
          console.log(div_id)
          if(rate<='2'){
              $('.reason-div').html(" ");
              var field = "<div class='row reason-div'>Reason<textarea id='reason-"+job+"' class='reason form-control' rows='4' name='reason'></textarea><div class='reason-error'></div></div>";
              $(form_id).append(field);
          }else{
              $('.reason-div').html(" ");
          }
      });

      $('body').on('click' , '.submit-rating', function(){
        var job = $(this).attr("id");
        var token = $("#token").val();
        var reason_id = "#reason-"+job;
        var reason = $(reason_id).val();
        var profile = $("input[name='profile']").val();
        var rate_id = 'input[name="rate-'+job+'"]:checked'
        var rate = $(rate_id).val();
        data_dict = {};
        if(profile){
          data_dict['user']=profile;
        }
        if(rate){
          data_dict['rating']=rate;
        }
        if(reason){
          data_dict['reason']=reason;
        }
        if(job){
            data_dict['job_type']=job;
          }
        console.log("reason_id", reason_id);
        console.log("reason", reason);
        console.log("data_dict", data_dict);
        if((rate>2)|((rate<=2)&(reason!=""))){
          $.ajax
          ({
              type: "POST",
              url: "/hobo_user/rate-user-api/",
              dataType: 'json',
              async: false,
              data: data_dict,
              beforeSend: function (xhr) {
                  xhr.setRequestHeader ("Authorization", token);
              },
              success: function(response){
                window.location.reload();
              }
          });
        }else{
          $('.reason-error').html("This field is required.");
        }
      });
