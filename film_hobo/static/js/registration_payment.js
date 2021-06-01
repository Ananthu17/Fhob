$( document ).ready(function() {
    $("#remove_promocode").hide();
    // $("#paypal-div").hide();

    var promotion_amount = localStorage.getItem("promotion_amount");
    if (promotion_amount){
        $('#promotion_amount').text(promotion_amount);
        $("#remove_promocode").show();
    }
    else{
        $("#remove_promocode").hide();
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
            localStorage.setItem('promotion_amount', parseFloat(response.data.promotion_amount));
            $('#final_amount').text(response.data.final_amount);
        }
    },(error) => {
        var title = "Promotion"
        var modal = $("#promocode_modal")
        modal.find('.modal-title').text(title)
        modal.find('.modal-body').text(JSON.parse(error.request.responseText).status)
        $("#promocode_modal").modal('show');
    });
});

$("#remove_promocode").click(function(){
    localStorage.removeItem("promotion_amount");
    $("#remove_promocode").remove();
    location.reload()
});
