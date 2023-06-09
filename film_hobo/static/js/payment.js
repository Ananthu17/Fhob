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
/*
get membership fee details and render to html
*/
if (localStorage.getItem("token")){
    var token = localStorage.getItem("token");
}
else{
    var new_token = getUrlParameter('token');
    var token = new_token.substring(0,new_token.length - 1)
}
token_str = "Token "
token_val = String(token)
var authorization_str = token_str.concat(token_val);
origin_url = window.location.origin
/*
delete discount record funtion
*/
function deleteDiscountFunction(obj_id) {
    var button_name = '#remove_btn' + obj_id
    var title = $(button_name).attr("data-title")
    var modal = $("#payment_admin_modal")
    var modal_text = "Are you sure you want to delete this discount?"
    modal.find('.modal-title').text(title)
    modal.find('.modal-body').text(modal_text)
    $("#modal_delete").attr("value", obj_id)
    $("#payment_admin_modal").modal('show');
}

$("#modal_delete").click(function(){
    origin_url = window.location.origin
    obj_id = $("#modal_delete").attr("value")
    delete_url = origin_url + '/payment/delete_discount_detail/' + obj_id + '/'
    axios.delete(delete_url, {headers: {'Authorization': authorization_str}})
    .then((response) => {
    if (response.status == 204){
            location.reload();
        }
    }, (error) => {
        console.log(error);
    });
});

var vaild_from_date = ""
var vaild_to_date = ""
function getVaildFrom(object)
{
    vaild_from_date = object.value
}
function getVaildTo(object)
{
    vaild_to_date = object.value
}

function editDiscountFunction(obj_id) {
    edit_field_element = '#modify_edit_' + obj_id
    edit_state = $(edit_field_element).text()
    if (edit_state === 'Edit'){
        $(edit_field_element).html("Save");

        editable_fields = 'edit' + obj_id
        var editable_elements = document.getElementsByClassName(editable_fields);
        for (var i = 0; i < editable_elements.length; i++) {
            element_to_change = editable_elements
            if (editable_elements.item(i).contentEditable == true) {
                editable_elements.item(i).contentEditable = false;
            } else {
                editable_elements.item(i).contentEditable = true;
            }
        }
        editable_elements.item(2).children[0].readOnly = false
        editable_elements.item(2).children[1].readOnly = false
    }
    else{
        editable_fields = 'edit' + obj_id
        var editable_elements = document.getElementsByClassName(editable_fields);
        edit_discount_url = origin_url + '/payment/edit_discount_detail/'

        for (var i = 0; i < editable_elements.length; i++) {
            promo_code_val = editable_elements.item(0).textContent
            amount_val = editable_elements.item(0).textContent

        }
        editable_fields = '.edit' + obj_id
        edtiable_date = '#valid_from_' + obj_id
        var edit_class = $(editable_fields);

        if (editable_elements[1].innerText.includes("$")){
            var amount_type_value = "flat_amount"
            var amount_value_value = editable_elements[1].innerText.replace(/[A-Za-z$-]/g, "")
        }
        else{
            var amount_type_value = "percentage"
            var amount_value_value = editable_elements[1].innerText.replace(new RegExp('%', 'g'),"")
        }

        if (vaild_from_date){
            vaild_from_date_final = vaild_from_date
        }
        else{
            vaild_from_date_final = $(editable_fields).find('input')[0].getAttribute("value");
        }

        if (vaild_to_date){
            vaild_to_date_final = vaild_to_date
        }
        else{
            vaild_to_date_final = $(editable_fields).find('input')[1].getAttribute("value");
        }

        edit_extra_args = {"id": obj_id,
                        "promo_code": editable_elements[0].innerText,
                        "valid_from": vaild_from_date_final,
                        "valid_to": vaild_to_date_final,
                        "amount_type": amount_type_value,
                        "amount": amount_value_value,
                        }

        axios.put(edit_discount_url, edit_extra_args, {headers: {'Authorization': authorization_str}})
        .then((response) => {
            if (response.status == 200){
                location.reload();
            }
        }, (error) => {
            console.log(error);
        });
    }
}

$( document ).ready(function() {
    origin_url = window.location.origin
    get_url = origin_url + '/payment/get_membership_fee_detail/'
    var token = localStorage.getItem("token");
    token_str = "Token "
    token_val = String(token)
    var authorization_str = token_str.concat(token_val);

    $("#annual_hobo").prop("readonly", true);
    $("#annual_indie").prop("readonly", true);
    $("#annual_pro").prop("readonly", true);
    $("#annual_company").prop("readonly", true);
    $("#monthly_hobo").prop("readonly", true);
    $("#monthly_indie").prop("readonly", true);
    $("#monthly_pro").prop("readonly", true);
    $("#monthly_company").prop("readonly", true);

    axios.get(get_url, {headers: {'Authorization': authorization_str}})
    .then((response) => {
        $('#annual_hobo').val("$ " + response.data.annual_hobo);
        $('#annual_indie').val("$ " + response.data.annual_indie);
        $('#annual_pro').val("$ " + response.data.annual_pro);
        $('#annual_company').val("$ " + response.data.annual_company);
        $('#monthly_hobo').val("$ " + response.data.monthly_hobo);
        $('#monthly_indie').val("$ " + response.data.monthly_indie);
        $('#monthly_pro').val("$ " + response.data.monthly_pro);
        $('#monthly_company').val("$ " + response.data.monthly_company);
        $('#annual_hobo_with_tax').val("$ " + response.data.annual_hobo_with_tax);
        $('#annual_indie_with_tax').val("$ " + response.data.annual_indie_with_tax);
        $('#annual_pro_with_tax').val("$ " + response.data.annual_pro_with_tax);
        $('#annual_company_with_tax').val("$ " + response.data.annual_company_with_tax);
        $('#monthly_hobo_with_tax').val("$ " + response.data.monthly_hobo_with_tax);
        $('#monthly_indie_with_tax').val("$ " + response.data.monthly_indie_with_tax);
        $('#monthly_pro_with_tax').val("$ " + response.data.monthly_pro_with_tax);
        $('#monthly_company_with_tax').val("$ " + response.data.monthly_company_with_tax);
        $('#tax_value').text(response.data.tax);
        $('#days_value').text(response.data.free_evaluation_time);
        var $renew_option = $('input:radio[name=renew_radio]');

        if (response.data.auto_renew === 'on'){
            $renew_option.filter('[id=on_click]').attr('checked', true);
            $renew_option.filter('[id=off_click]').attr('disabled', true);
        }
        else if (response.data.auto_renew === 'off'){
            $renew_option.filter('[id=off_click]').attr('checked', true);
            $renew_option.filter('[id=on_click]').attr('disabled', true);
        }
        else{
            $renew_option.filter('[id=on_click]').attr('checked', false);
            $renew_option.filter('[id=off_click]').attr('checked', false);
            $renew_option.filter('[id=on_click]').attr('disabled', true);
            $renew_option.filter('[id=off_click]').attr('disabled', true);
        }
    });
    $('#datepicker').prop('readonly', true);

    // data to load if the promo-code is added via client side
    get_lust_url = origin_url + '/payment/get_discount_detail_list/'

    axios.get(get_lust_url, {headers: {'Authorization': authorization_str}})
    .then((response) => {
      discount_objs = response.data

      let table = '<thead> <tr> <th>Discount Name</th> <th>Amount</th> <th>Timeframe</th> <th colspan="2">Action</th> </tr></thead><tbody></tbody>';
        discount_objs.forEach(function(d){
        obj_id = d.id
        if (d.amount_type == "flat_amount"){
            var amount_value = '$ ' + (d.amount).toString()
        }
        else{
            var amount_value = (d.amount).toString() + ' %'
        }
        delete_url = origin_url + '/payment/delete_discount_detail/' + d.id
        table += '<tr><td contenteditable="false" class="edit'+d.id+'">'+d.promo_code+'</td>';
        table += '<td contenteditable="false" class="edit'+d.id+'">'+amount_value+'</td>';
        table += '<td contenteditable="false" class="edit'+d.id+'"><input id="valid_from_'+d.id+'" type="date" onkeydown="return false" class="form-control admin-bill-form-cntrl-b w-42 date-class" value = "'+d.valid_from+'" onchange="getVaildFrom(this);" readonly />to<input id="valid_to_'+d.id+'" type="date" onkeydown="return false" class="form-control admin-bill-form-cntrl-b w-42 date-class" value = "'+d.valid_to+'" onchange="getVaildTo(this);" readonly/> </td>';
        table += '<td><a id="remove_btn'+d.id+'" class="modify_remove_id admin-bill-link" data-toggle="modal" data-target="#payment_admin_modal" alt="modify_remove" value="'+d.id+'" href="#" onclick="return deleteDiscountFunction('+obj_id+')" data-title="Remove Discount">Remove</a></td><td> <a id="modify_edit_'+d.id+'" alt="modify_edit" class="admin-bill-link" href="#" onclick="return editDiscountFunction('+obj_id+')">Edit</a></td></tr>';
    })
      table += '</tbody>';
      $('#discount_table').empty().html(table);
    });

    // data to load if the promo-code from the braintree
    // get_braintree_discounts = origin_url + '/payment/braintree/get_discount_details/'

    // axios.get(get_braintree_discounts, {headers: {'Authorization': authorization_str}})
    // .then((response) => {
    //   discount_objs = response.data

    //   let table = '<thead> <tr> <th>Braintree ID</th> <th>Promocode (Name)</th> <th>Description</th><th>Amount</th><th>Number of Billing Cycles</th></tr></thead><tbody></tbody>';
    //     discount_objs.forEach(function(d){
    //     obj_id = d.braintree_id
    //     if (d.billing_cycles == null){
    //         var billing_cycles_dur = 'For Duration of Subscription'
    //     }
    //     else{
    //         var billing_cycles_dur = d.billing_cycles
    //     }
    //     table += '<tr><td contenteditable="false" class="edit'+d.braintree_id+'">'+d.braintree_id+'</td>';
    //     table += '<td contenteditable="false" class="edit'+d.braintree_id+'">'+d.promo_code+'</td>';
    //     table += '<td contenteditable="false" class="edit'+d.braintree_id+'">'+d.description+'</td>';
    //     table += '<td contenteditable="false" class="edit'+d.braintree_id+'">'+d.amount+'</td>';
    //     table += '<td contenteditable="false" class="edit'+d.braintree_id+'">'+billing_cycles_dur+'</td>';
    // })
    //   table += '</tbody>';
    //   $('#braintree_discount_table').empty().html(table);
    // });
});
/*
make the table column field editable
*/
document.getElementById("membership_fee_edit").addEventListener("click", function() {
    // if ($('#annual_hobo').is('[readonly]')) {
    //     $("#annual_hobo").prop("readonly", false);
    // } else {
    //     $("#annual_hobo").prop("readonly", true);
    // }

    if ($('#annual_indie').is('[readonly]')) {
        $("#annual_indie").prop("readonly", false);
    } else {
        $("#annual_indie").prop("readonly", true);
    }

    if ($('#annual_pro').is('[readonly]'))  {
        $("#annual_pro").prop("readonly", false);
    } else {
        $("#annual_pro").prop("readonly", true);
    }

    if ($('#annual_company').is('[readonly]')) {
        $("#annual_company").prop("readonly", false);
    } else {
        $("#annual_company").prop("readonly", true);
    }

    // if ($('#monthly_hobo').is('[readonly]')) {
    //     $("#monthly_hobo").prop("readonly", false);
    // } else {
    //     $("#monthly_hobo").prop("readonly", true);
    // }

    if ($('#monthly_indie').is('[readonly]')) {
        $("#monthly_indie").prop("readonly", false);
    } else {
        $("#monthly_indie").prop("readonly", true);
    }

    if ($('#monthly_pro').is('[readonly]')) {
        $("#monthly_pro").prop("readonly", false);
    } else {
        $("#monthly_pro").prop("readonly", true);
    }

    if ($('#monthly_company').is('[readonly]')) {
        $("#monthly_company").prop("readonly", false);
    } else {
        $("#monthly_company").prop("readonly", true);
    }

    if ($("#tax_value").attr("contenteditable") == "true") {
      $("#tax_value").attr("contenteditable", "false");
    } else {
        $("#tax_value").attr("contenteditable", "true");
    }

    if ($("#days_value").attr("contenteditable") == "true") {
        $("#days_value").attr("contenteditable", "false");
    } else {
        $("#days_value").attr("contenteditable", "true");
        $('#on_click').removeAttr("disabled");
        $('#off_click').removeAttr("disabled");
    }
});
/*
post membership fee details and render to html
*/
document.getElementById("membership_fee_save").addEventListener("click", function() {
    var renew_option = $('input:radio[name=renew_radio]');
    var selected_option_name = "";
    if (renew_option[0].checked == true){
        var selected_option_name = "on";
    }
    else if (renew_option[1].checked == true){
        var selected_option_name = "off";
    }
    else{

    }

    put_url = origin_url + '/payment/update_membership_fee/'
    extra_args = {
        "monthly_hobo": $("#monthly_hobo").val().replace(/[A-Za-z$-]/g, ""),
        "monthly_indie": $("#monthly_indie").val().replace(/[A-Za-z$-]/g, ""),
        "monthly_pro": $("#monthly_pro").val().replace(/[A-Za-z$-]/g, ""),
        "monthly_company": $("#monthly_company").val().replace(/[A-Za-z$-]/g, ""),
        "annual_hobo": $("#annual_hobo").val().replace(/[A-Za-z$-]/g, ""),
        "annual_indie": $("#annual_indie").val().replace(/[A-Za-z$-]/g, ""),
        "annual_pro": $("#annual_pro").val().replace(/[A-Za-z$-]/g, ""),
        "annual_company": $("#annual_company").val().replace(/[A-Za-z$-]/g, ""),
        "tax": $('span[id="tax_value"]').text(),
        "free_evaluation_time": $('span[id="days_value"]').text(),
        "auto_renew": selected_option_name
    }
    var token = localStorage.getItem("token");
    token_str = "Token "
    token_val = String(token)
    var authorization_str = token_str.concat(token_val);

    plan_id_url =  origin_url + '/payment/get_paypal_plan_id'

    axios.get(plan_id_url, {headers: { "Authorization": authorization_str}})
    .then((response) => {
        if (response.status == 200){

            var plan_id_indie_payment_monthly = response.data.indie_payment_monthly
            var plan_id_indie_payment_yearly = response.data.indie_payment_yearly
            var plan_id_pro_payment_monthly = response.data.pro_payment_monthly
            var plan_id_pro_payment_yearly = response.data.pro_payment_yearly
            var plan_id_company_payment_monthly = response.data.company_payment_monthly
            var plan_id_company_payment_yearly = response.data.company_payment_yearly

            indie_payment_monthly_patch_url = "https://api-m.sandbox.paypal.com/v1/billing/plans/" + plan_id_indie_payment_monthly + "/update-pricing-schemes"
            indie_payment_yearly_patch_url = "https://api-m.sandbox.paypal.com/v1/billing/plans/" + plan_id_indie_payment_yearly + "/update-pricing-schemes"
            pro_payment_monthly_patch_url = "https://api-m.sandbox.paypal.com/v1/billing/plans/" + plan_id_pro_payment_monthly + "/update-pricing-schemes"
            pro_payment_yearly_patch_url = "https://api-m.sandbox.paypal.com/v1/billing/plans/" + plan_id_pro_payment_yearly + "/update-pricing-schemes"
            company_payment_monthly_patch_url = "https://api-m.sandbox.paypal.com/v1/billing/plans/" + plan_id_company_payment_monthly + "/update-pricing-schemes"
            company_payment_yearly_patch_url = "https://api-m.sandbox.paypal.com/v1/billing/plans/" + plan_id_company_payment_yearly + "/update-pricing-schemes"

            var indie_payment_monthly_args = {
                "pricing_schemes": [{
                    "billing_cycle_sequence": 1,
                    "pricing_scheme": {
                    "fixed_price": {
                        "value": String(extra_args.monthly_indie.trim()),
                        "currency_code": "USD"
                        }
                    }
                    }
                ]
            }

            var indie_payment_yearly_args = {
                "pricing_schemes": [{
                    "billing_cycle_sequence": 1,
                    "pricing_scheme": {
                    "fixed_price": {
                        "value": String(extra_args.annual_indie.trim()),
                        "currency_code": "USD"
                        }
                    }
                    }
                ]
            }

            var pro_payment_monthly_args = {
                "pricing_schemes": [{
                    "billing_cycle_sequence": 1,
                    "pricing_scheme": {
                    "fixed_price": {
                        "value": String(extra_args.monthly_pro.trim()),
                        "currency_code": "USD"
                        }
                    }
                    }
                ]
            }

            var pro_payment_yearly_args = {
                "pricing_schemes": [{
                    "billing_cycle_sequence": 1,
                    "pricing_scheme": {
                    "fixed_price": {
                        "value": String(extra_args.annual_pro.trim()),
                        "currency_code": "USD"
                        }
                    }
                    }
                ]
            }

            var company_payment_monthly_args = {
                "pricing_schemes": [{
                    "billing_cycle_sequence": 1,
                    "pricing_scheme": {
                    "fixed_price": {
                        "value": String(extra_args.monthly_company.trim()),
                        "currency_code": "USD"
                        }
                    }
                    }
                ]
            }

            var company_payment_yearly_args = {
                "pricing_schemes": [{
                    "billing_cycle_sequence": 1,
                    "pricing_scheme": {
                    "fixed_price": {
                        "value": String(extra_args.annual_company.trim()),
                        "currency_code": "USD"
                        }
                    }
                    }
                ]
            }

            get_access_token_url = origin_url + '/payment/get_paypal_token'
            send_plan_change_email_url = origin_url + '/payment/paypal/send_plan_change_email/'
            axios.post(get_access_token_url)
            .then((response) => {
                var paypal_access_token = "Bearer " + response.data.access_token

                axios.post(indie_payment_monthly_patch_url, indie_payment_monthly_args, {headers: {'Content-Type': 'application/json', 'Authorization': paypal_access_token}})
                .then((response) => {
                if ((response.status == 204) || (response.status == 422)) {

                        var send_plan_change_email_url_args = {
                            "changed_plan_id": plan_id_indie_payment_monthly,
                        }

                        axios.post(send_plan_change_email_url, send_plan_change_email_url_args, {headers: {'Content-Type': 'application/json', 'Authorization': paypal_access_token}})
                        .then((response) => {
                            console.log("response:::")
                            console.log(plan_id_indie_payment_monthly)
                        }, (error) => {
                            console.log(error);
                        });

                        console.log(response);
                    }
                }, (error) => {
                    console.log(error);
                });

                axios.post(indie_payment_yearly_patch_url, indie_payment_yearly_args, {headers: {'Content-Type': 'application/json', 'Authorization': paypal_access_token}})
                .then((response) => {
                if ((response.status == 204) || (response.status == 422)) {
                        console.log(response);
                    }
                }, (error) => {
                    console.log(error);
                });

                axios.post(pro_payment_monthly_patch_url, pro_payment_monthly_args, {headers: {'Content-Type': 'application/json', 'Authorization': paypal_access_token}})
                .then((response) => {
                if ((response.status == 204) || (response.status == 422)) {
                        console.log(response);
                    }
                }, (error) => {
                    console.log(error);
                });

                axios.post(pro_payment_yearly_patch_url, pro_payment_yearly_args, {headers: {'Content-Type': 'application/json', 'Authorization': paypal_access_token}})
                .then((response) => {
                if ((response.status == 204) || (response.status == 422)) {
                        console.log(response);
                    }
                }, (error) => {
                    console.log(error);
                });

                axios.post(company_payment_monthly_patch_url, company_payment_monthly_args, {headers: {'Content-Type': 'application/json', 'Authorization': paypal_access_token}})
                .then((response) => {
                if ((response.status == 204) || (response.status == 422)) {
                        console.log(response);
                    }
                }, (error) => {
                    console.log(error);
                });

                axios.post(company_payment_yearly_patch_url, company_payment_yearly_args, {headers: {'Content-Type': 'application/json', 'Authorization': paypal_access_token}})
                .then((response) => {
                if ((response.status == 204) || (response.status == 422)) {
                        console.log(response);
                    }
                }, (error) => {
                    console.log(error);
                });

            }, (error) => {
                console.log(error);
            });

        }
    }).catch(function(error)
    {
        console.log(error.response);
    });

    axios.put(put_url, extra_args, {headers: {'Authorization': authorization_str}})
    .then((response) => {
        // location.reload();
    }, (error) => {
        console.log(error);
    });

});
/*
toggle the text in amount (Add active class to the current button (highlight it))
*/
var header = document.getElementById("discount_amount");
var btns = header.getElementsByClassName("toggle_dp");
for (var i = 0; i < btns.length; i++) {
  btns[i].addEventListener("click", function() {
  var current = document.getElementsByClassName("dp_active_toggle");
  current[0].className = current[0].className.replace(" dp_active_toggle", "");
  this.className += " dp_active_toggle";
  var final_str = current[0].innerText
  $('#doller-percentage-toggle').html(final_str);
});
}
/*
get details of new discount and pass to add discount api
*/
document.getElementById("discount_add").addEventListener("click", function() {
    
    add_url = origin_url + '/payment/add_discount_detail/'

    var amount_type_val = ""
    if ($("#doller-percentage-toggle").text() == "$"){
        console.log($("#doller-percentage-toggle").text())
        var amount_type_val = "flat_amount"
        console.log(amount_type_val)
    }
    else {
        var amount_type_val = "percentage"
        console.log(amount_type_val)
    }

    var add_args = {
        "promo_code": document.getElementById("discount_name_input").value,
        "valid_from": document.getElementById("valid_from").value,
        "valid_to": document.getElementById("valid_to").value,
        "amount_type": amount_type_val,
        "amount": document.getElementById("discount_amount_input").value,
    }
    console.log(add_args)
    console.log(authorization_str)
    console.log(add_url)
    axios.post(add_url, add_args, {headers: { "Authorization": authorization_str}})
    .then((response) => {
        if (response.status == 200){
            location.reload();
        }
    }, (error) => {
        console.log(error);
    });

});