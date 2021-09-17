$( document ).ready(function() {
    $("#remove_promocode").hide();
    // $("#paypal-div").hide();
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
    }

    if(window.location.href.indexOf("pro") != -1){
        $('#center_btn_text').text("Pro");
    }

    if(window.location.href.indexOf("company") != -1){
        $('#center_btn_text').text("Company");
    }

    // check if the user is beta user and
    var betacode = localStorage.getItem("beta-code");
    if (betacode){
        
    }

});

$("#apply_promocode").click(function(){
    // var title = "Promotion"
    // var modal = $("#promocode_modal")
    // var modal_success_text = "Promocode Applied Successfully"
    // var modal_failure_text = "Invalid Promocode"
    // modal.find('.modal-title').text(title)
    // modal.find('.modal-body').text(modal_success_text)
    // $("#promocode_modal").modal('show');

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