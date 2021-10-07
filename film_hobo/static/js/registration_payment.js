origin_url = window.location.origin
get_beta_tester_code_id_url = origin_url + "/hobo_user/get-beta-tester-code-id/"

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

$( document ).ready(function() {
    $("#remove_promocode").hide();
    localStorage.setItem('promocode', '');
    localStorage.setItem('promotion_amount', '');
    localStorage.setItem('final_amount', '');
    var promotion_amount = localStorage.getItem("promotion_amount");
    var final_amount = localStorage.getItem("final_amount");
    if (promotion_amount){
        $('#promotion_amount').text(promotion_amount);
        $('#final_amount').text(final_amount);
        $("#remove_promocode").show();
    }
    else{
        $("#remove_promocode").hide();
    }

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

    // check if the user is beta user and
    var betacode = getUrlParameter('beta_code');
    if (betacode){
        // check if beta-user code is valid
        check_beta_tester_code_args = {"code": betacode}
        check_beta_tester_code_api = origin_url + '/hobo_user/check-beta-tester-code/'
        axios.post(check_beta_tester_code_api, check_beta_tester_code_args)
        .then((response) => {
            if (response.status == 200){
                // get the beta user plan details
                get_beta_user_plan_details_api = origin_url + '/payment/get_beta_user_plan_details'
                time_period = $("#payment_plan").text();
                extra_args = {"code": betacode,
                              "membership": membership,
                              "period": time_period}
                axios.post(get_beta_user_plan_details_api, extra_args)
                .then((response) => {
                    var bill_date = response.data.bill_date
                    var days = response.data.days
                    $("#bill_start_date").text(bill_date);
                    $("#days_free").text(days);
                }, (error) => {
                    console.log(error);
                });
            }
        }, (error) => {
            console.log(error);
        });
    }
});

$("#apply_promocode").click(function(){
    origin_url = window.location.origin
    get_url = origin_url + '/payment/get_membership_fee_detail/'
    var token = localStorage.getItem("token");
    token_str = "Token "
    token_val = String(token)
    var authorization_str = token_str.concat(token_val);

    calculate_discount_url = origin_url + '/payment/calculate_discount/'
    calculate_discount_args = {
        "amount": $("#full_amount").text(),
        "promocode": $("#promocode").val()
    }
    axios.post(calculate_discount_url, calculate_discount_args)
    .then((response) => {
        if (response.status == 200){
            $('#promocode').val('');
            $("#remove_promocode").show();
            var title = "Promotion"
            var modal = $("#promocode_modal")
            var modal_success_text = "Promocode Applied Successfully"
            modal.find('.modal-title').text(title)
            modal.find('.modal-body').text(modal_success_text)
            $("#promocode_modal").modal('show');
            $('#full_amount').text(response.data.initial_amount);
            $('#promotion_amount').text(response.data.promotion_amount);
            localStorage.setItem('promocode', response.data.promocode);
            localStorage.setItem('promotion_amount', parseFloat(response.data.promotion_amount));
            localStorage.setItem('final_amount', parseFloat(response.data.final_amount));
            $('#final_amount').text(response.data.final_amount);
        }
    },(error) => {
        var title = "Promotion"
        var modal = $("#promocode_modal")
        modal.find('.modal-title').text(title)
        modal.find('.modal-body').text(JSON.parse(error.request.responseText).status)
        $("#promocode_modal").modal('show');
    });

    // braintree_calculate_discount_url = origin_url + '/payment/braintree/calculate_discount/'
    // calculate_discount_args = {
    //     "amount": $("#full_amount").text(),
    //     "promocode": $("#promocode").val()
    // }
    // axios.post(braintree_calculate_discount_url, calculate_discount_args)
    // .then((response) => {
    //     if (response.status == 200){
    //         $('#promocode').val('');
    //         $("#remove_promocode").show();
    //         var title = "Promotion"
    //         var modal = $("#promocode_modal")
    //         var modal_success_text = "Promocode Applied Successfully"
    //         modal.find('.modal-title').text(title)
    //         modal.find('.modal-body').text(modal_success_text)
    //         $("#promocode_modal").modal('show');
    //         $('#full_amount').text(response.data.initial_amount);
    //         $('#promotion_amount').text(response.data.promotion_amount);
    //         localStorage.setItem('promocode', response.data.promocode);
    //         localStorage.setItem('promotion_amount', parseFloat(response.data.promotion_amount));
    //         localStorage.setItem('final_amount', parseFloat(response.data.final_amount));
    //         $('#final_amount').text(response.data.final_amount);
    //     }
    // },(error) => {
    //     var title = "Promotion"
    //     var modal = $("#promocode_modal")
    //     modal.find('.modal-title').text(title)
    //     modal.find('.modal-body').text(JSON.parse(error.request.responseText).status)
    //     $("#promocode_modal").modal('show');
    // });
});

$("#remove_promocode").click(function(){
    localStorage.removeItem("promocode");
    localStorage.removeItem("promotion_amount");
    localStorage.removeItem("final_amount");
    $("#remove_promocode").remove();
    location.reload()
});


$("#modal_cancel").click(function(){
    $("#promocode_modal").modal("hide");
});

$("#modal_cancel_cross").click(function(){
    $("#promocode_modal").modal("hide");
});

// paypal_get_new_plan_details_url = origin_url +'/payment/paypal/get_new_plan_details/'
// paypal_get_new_plan_details_args = {
//   "plan_type": "",
//   "plan_tenure": $("#payment_plan").text(),
//   "applied_promocode": "",
//   "final_new_amount": ""
// }


// axios.post(paypal_get_new_plan_details_url, paypal_get_new_plan_details_args)
// .then((response) => {
//     if (response.status == 200){
//     }
// },(error) => {
// });