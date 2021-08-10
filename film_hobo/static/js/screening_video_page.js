origin_url = window.location.origin

$('#share-link').click(function(event){
    var modal = $("#shareModal")
    var title = "Share to"
    modal.find('.modal-title').text(title)
    $("#shareModal").modal('show');
});

var token = $("#token")
var token_auth_str = token.val()

get_friends_list_url = origin_url + '/hobo_user/list-all-friend-api/'
axios.get(get_friends_list_url, {headers: { 'Authorization': token_auth_str }})
.then((response) => {
    var friends_obj = response.data.friends
    var validOptions = [];
    $.each(friends_obj, function(key_1,valueObj_1){
        $.each(valueObj_1, function(key_2,valueObj_2){
            if (key_2 === "user"){
                validOptions.push(valueObj_2);
            }
        });
    });

    previousValue = "";

    $('#enter_email').autocomplete({
        source: validOptions
    }).keyup(function() {
        var isValid = false;
        for (i in validOptions) {
            if (validOptions[i].toLowerCase().match(this.value.toLowerCase())) {
                isValid = true;
            }
        }
        if (!isValid) {
            this.value = previousValue
        } else {
            previousValue = this.value;
        }
    });

}, (error) => {
    console.log(error);
});

$('#invite_send').click(function(event){
    var email = $("#all_mail")
    for ( var i = 0, l = email.length; i < l; i++ ) {
        var to_send_email = email.children()[i].innerText.slice(0,-2)
        console.log(to_send_email)
    }
    // var to_send_email = email.children()[0].innerText.slice(0,-2)
    var url_to_share = window.location.origin + window.location.pathname

    invite_url = window.location.origin + '/hobo_user/user_home/invite/'

    invite_url_args = {
        "to_user_email": to_send_email,
        "project_url": url_to_share,
    }

    axios.post(invite_url, invite_url_args, {headers: { 'Authorization': token_auth_str }})
    .then((response) => {
        console.log(response);
    }, (error) => {
        console.log(error);
    });

});

$('#share-close-btn').click(function(event){
    $("#shareModal").modal('hide');
});

$('#share-close-cross').click(function(event){
    $("#shareModal").modal('hide');
});

// get_friends_list_url = origin_url + '/payment/paypal/create/'

// $('#invite-link').click(function(event){
//     var modal = $("#inviteModal")
//     var title = "Invite to"
//     modal.find('.modal-title').text(title)
//     $("#inviteModal").modal('show');

//     axios.get(get_friends_list_url)
//     .then((response) => {
//         plan_id = response.data.plan_id
//     }, (error) => {
//         console.log(error);
//     });

// });

$('#shareModalClose').click(function(event){
    $("#shareModal").modal('hide');
});


$('#inviteModalClose').click(function(event){
    $("#inviteModal").modal('hide');
});

$('#cancel_invite_btn').click(function(event){
    $("#inviteModal").modal('hide');
});