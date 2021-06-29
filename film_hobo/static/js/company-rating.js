
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

$("input[name='rate']").change(function(){
    var rate = $('input[name="rate"]:checked').val();
    if(rate<='2'){
        $('.reason-div').html(" ");
        var field = "<div class='row reason-div'>Reason<textarea class='reason form-control' rows='4' name='reason'></textarea><div class='reason-error'></div></div>";
        $('.rating-form').append(field);
    }else{
        $('.reason-div').html(" ");
    }
});

$('body').on('click' , '.submit-rating', function(){
  var profile = $(this).attr("id");
  var token = $("#token").val();
  var rate = $('input[name="rate"]:checked').val();
  var reason = $('.reason').val();
  data_dict = {};
  if(profile){
    data_dict['company']=profile;
  }
  if(rate){
    data_dict['rating']=rate;
  }
  if(reason){
    data_dict['reason']=reason;
  }
  if((rate>2)|((rate<=2)&(reason!=""))){
    $.ajax
    ({
        type: "POST",
        url: "/hobo_user/rate-company-api/",
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

