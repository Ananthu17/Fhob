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

paypal.Buttons({
createOrder: function() {
        transaction_args = {
        "token": localStorage.getItem("token"),
        "days_free": $("#days_free").text(),
        "payment_plan": $("#payment_plan").text(),
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
        return res.json();
    }).then(function(data) {
        return data.id; // Use the key sent by your server's response, ex. 'id' or 'token'
    });
},

onApprove: function(data) {
    capture_url = origin_url + '/payment/paypal/' + data.orderID + '/capture/'
    success_redirect = origin_url + '/hobo_user/user_login/'
    return fetch(capture_url, {
        method: 'post',
        headers: {
            'content-type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
        orderID: data.orderID
        })
    }).then(function(res) {
        return res.json();
    }).then(function(details) {
        console.log(details)
        transaction_username = details.payer.name.given_name + ' ' + details.payer.name.surname
        alert('Transaction funds captured from ' + transaction_username);
        var delay = 1000;
        setTimeout(function(){ window.location = success_redirect; }, delay);
    })
}

}).render('#paypal-div'); // Display payment options on your web page

// If this returns false or the card fields aren't visible, see Step #1.
if (paypal.HostedFields.isEligible()) {
    // Renders card fields
    paypal.HostedFields.render({
        // Call your server to set up the transaction
        createOrder: function() {
            return fetch('/your-server/paypal/order', {
                method: 'post'
            }).then(function(res) {
                return res.json();
            }).then(function(orderData) {
                orderId = orderData.id;
                return orderId;
            });
        },

        styles: {
            '.valid': {
                'color': 'green'
            },
            '.invalid': {
                'color': 'red'
            }
        },

        fields: {
            number: {
                selector: "#card-number",
                placeholder: "4111 1111 1111 1111"
            },
            cvv: {
                selector: "#cvv",
                placeholder: "123"
            },
            expirationDate: {
                selector: "#expiration-date",
                placeholder: "MM/YY"
            }
        }
    }).then(function(cardFields) {
        document.querySelector("#card-form").addEventListener('submit', (event) => {
            event.preventDefault();

            cardFields.submit({
                // Cardholder's first and last name
                cardholderName: document.getElementById('card-holder-name').value,
                // Billing Address
                billingAddress: {
                    // Street address, line 1
                    streetAddress: document.getElementById('card-billing-address-street').value,
                    // Street address, line 2 (Ex: Unit, Apartment, etc.)
                    extendedAddress: document.getElementById('card-billing-address-unit').value,
                    // State
                    region: document.getElementById('card-billing-address-state').value,
                    // City
                    locality: document.getElementById('card-billing-address-city').value,
                    // Postal Code
                    postalCode: document.getElementById('card-billing-address-zip').value,
                    // Country Code
                    countryCodeAlpha2: document.getElementById('card-billing-address-country').value
                }
            }).then(function() {
                // Payment was successful! Show a notification or redirect to another page.
                window.location.replace('http://www.somesite.com/review');
            }).catch(function(err) {
                alert('Payment could not be captured! ' + JSON.stringify(err))
            });
        });
    });
}
else {
    // Hides card fields if the merchant isn't eligible
    document.querySelector("#card-form").style = 'display: none';
}