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

var button = document.querySelector('#submit-button');

braintree.dropin.create({
  authorization: 'sandbox_gp898zyf_yqck57s94b3kb9cv',
  selector: '#dropin-container'
}, function (err, instance) {
  button.addEventListener('click', function () {
    instance.requestPaymentMethod(function (err, payload) {
      var email = getUrlParameter('email');
      result = {
        "amount": $("#final_amount").text(),
        "payment_method_nonce": payload.nonce,
        "submit_for_settlement": true,
        "email": email
      }

      origin_url = window.location.origin
      post_url = origin_url + '/payment/braintree/initial_request/'
      axios.post(post_url, JSON.stringify(result), {headers: { 'Content-Type': 'application/json' }})
      .then((response) => {
        console.log(response);
        debugger
      }, (error) => {
        debugger
        console.log(error);
      });

    });
  })
});