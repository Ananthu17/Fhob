var getUrlParameter = function getUrlParameter(sParam) {
  var sPageURL = window.location.search.substring(1),
      sURLVariables = sPageURL.split('&'),
      sParameterName,
      i;

  for (i = 0; i < sURLVariables.length; i++) {
      sParameterName = sURLVariables[i].split('=');

      if (sParameterName[0] === sParam) {
          return typeof sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
      }
  }
  return false;
};

var token = localStorage.getItem("token");
subscription_details_url = origin_url + '/payment/braintree_subscription_details'
braintree_subscription_details_args = {
    "token": token,
    "payment_plan": $("#payment_plan").text(),
}

var braintree_plan_id = ""

axios.post(subscription_details_url, braintree_subscription_details_args)
.then((response) => {
    braintree_plan_id = response.data.plan_id
}, (error) => {
    console.log(error);
});


var button = document.querySelector('#submit-button');
if (localStorage.getItem("promocode")){
  applied_promo = localStorage.getItem("promocode")
}
else{
  applied_promo = ""
}

braintree.dropin.create({
  authorization: 'sandbox_gp898zyf_yqck57s94b3kb9cv',
  selector: '#dropin-container'
}, function (err, instance) {
  button.addEventListener('click', function () {
    instance.requestPaymentMethod(function (err, payload) {
      var email = getUrlParameter('email');
      debugger
      result = {
        "amount": $("#final_amount").text(),
        "payment_method_nonce": payload.nonce,
        "submit_for_settlement": true,
        "email": email,
        "braintree_plan_id": braintree_plan_id,
        "days_free": $("#days_free").text(),
        "payment_plan": $("#payment_plan").text(),
        "payment_method": "card_payment",
        "initial_amount": $("#initial_amount_val").text(),
        "tax_applied": $("#tax_percentage").text(),
        "promocodes_applied": applied_promo,
        "promotion_amount": $("#promotion_amount").text(),
      }

      origin_url = window.location.origin
      post_url = origin_url + '/payment/braintree/initial_request/'
      success_redirect = origin_url + '/hobo_user/user_login/'
      axios.post(post_url, JSON.stringify(result), {headers: { 'Content-Type': 'application/json' }})
      .then((response) => {
        $('#payment-success-div').show();
        var delay = 1000;
        setTimeout(function(){ window.location = success_redirect; }, delay);
      }, (error) => {
        $('#payment-success-div').replaceWith(
          '<div class="alert alert-danger">Subscription Unsuccessful, Please try again.</div>'
          );
      });

    });
  })
});