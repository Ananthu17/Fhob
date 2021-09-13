$(document).ready(function() {
    $('#payment-success-div').hide();
});

origin_url = window.location.origin
create_url = origin_url + '/payment/paypal/create/'
var token = localStorage.getItem("token");
token_str = "Token "
token_val = String(token)
var authorization_str = token_str.concat(token_val);

if (localStorage.getItem("promocode")){
    applied_promo = localStorage.getItem("promocode")
}
else{
    applied_promo = ""
}

function getCookie(name) {
let cookieValue = null;
if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
    }
}
return cookieValue;
}
const csrftoken = getCookie('csrftoken');

let orderId;


subscription_details_url = origin_url + '/payment/subscription_details'
subscription_details_args = {
    "token": token,
    "payment_plan": $("#payment_plan").text(),
}

var plan_id = ""

axios.post(subscription_details_url, subscription_details_args)
.then((response) => {
    plan_id = response.data.plan_id
}, (error) => {
    console.log(error);
});

const headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer Access-Token',
    'Content-Type': 'application/json',
  }

success_redirect = origin_url + '/hobo_user/user_login/'
paypal.Buttons({

createSubscription: function(data, actions) {

    return actions.subscription.create({

        'plan_id': plan_id

    });
},

onApprove: function(data, actions) {
    transaction_args = {
        "token": localStorage.getItem("token"),
        "days_free": $("#days_free").text(),
        "payment_plan": $("#payment_plan").text(),
        "payment_method": "paypal_account",
        "initial_amount": $("#initial_amount_val").text(),
        "tax_applied": $("#tax_percentage").text(),
        "promocodes_applied": applied_promo,
        "promotion_amount": $("#promotion_amount").text(),
        "final_amount": $("#final_amount").text(),
    }

    return fetch(create_url, {
        method: 'post',
        headers: {
            'content-type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(transaction_args),
    }).then(function(res) {
        alert('You have successfully created subscription ' + data.subscriptionID);
        var delay = 1000;
        setTimeout(function(){ window.location = success_redirect; }, delay);
    }).then(function(data) {
        return data.id;
    });

  },

    // // add this incase want to hide the debit/credit card option
    // style: {
    //     layout: 'horizontal',
    //     tagline: 'false'
    // }

}).render('#paypal-div'); // Display payment options on your web page
