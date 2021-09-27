$(document).ready(function() {
    $('#payment-success-div').hide();
});

origin_url = window.location.origin
create_url = origin_url + '/payment/paypal/create/'
send_email_url = origin_url + '/payment/paypal/send_email_recepit/'
sendSuccessEmail()
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

if(window.location.href.indexOf("indie") != -1){
    $('#center_btn_text').text("Indie");
    var membership = 'indie'
}

if(window.location.href.indexOf("pro") != -1){
    $('#center_btn_text').text("Pro");
    var membership = 'pro'
}

if(window.location.href.indexOf("company") != -1){
    $('#center_btn_text').text("Company");
    var membership = 'company'
}

var betacode = getUrlParameter('beta_code');
if(betacode){
    beta_plan_details_api = origin_url + '/payment/get_beta_user_plan_details'
    time_period = $("#payment_plan").text();
    extra_args = {"code": betacode,
                  "membership": membership,
                  "period": time_period}
    axios.post(beta_plan_details_api, extra_args)
    .then((response) => {
        var bill_date = response.data.bill_date
        var days = response.data.days
        var selected_plan_id = response.data.selected_plan_id
        $("#bill_start_date").text(bill_date);
        $("#days_free").text(days);
        var plan_id = selected_plan_id
        localStorage.setItem('plan_id', plan_id);
    }, (error) => {
        console.log(error);
    })
}
else{
    subscription_details_url = origin_url + '/payment/subscription_details'
    subscription_details_args = {
        "token": token,
        "payment_plan": $("#payment_plan").text(),
    }

    var plan_id = ""

    axios.post(subscription_details_url, subscription_details_args)
    .then((response) => {
        plan_id = response.data.plan_id
        localStorage.setItem('plan_id', plan_id);
    }, (error) => {
        console.log(error);
    });
}
var plan_id_final = localStorage.getItem("plan_id");

const headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer Access-Token',
    'Content-Type': 'application/json',
  }

success_redirect = origin_url + '/hobo_user/user_login/'
paypal.Buttons({

createSubscription: function(data, actions) {

    return actions.subscription.create({

        'plan_id': plan_id_final

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
        sendSuccessEmail(data)
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

// function sendSuccessEmail(data)
function sendSuccessEmail()
{
    debugger
    // var order_id = data.orderID
    var order_id = "0HD29369C3915992L"
    send_email_url_args = {
        "order_id": order_id
    }

    axios.post(send_email_url, send_email_url_args)
    .then((response) => {
        debugger
        console.log(response);
    }, (error) => {
        debugger
        console.log(error);
    });
}
