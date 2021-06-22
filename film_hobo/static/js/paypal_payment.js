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

paypal.Buttons({

createSubscription: function(data, actions) {

    return actions.subscription.create({

        'plan_id': plan_id

    });
},

onApprove: function(data, actions) {

    alert('You have successfully created subscription ' + data.subscriptionID);

  }

}).render('#paypal-div'); // Display payment options on your web page

