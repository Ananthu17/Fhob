origin_url = window.location.origin

$('#share-link').click(function(event){
    var modal = $("#shareModal")
    var title = "Share to"
    modal.find('.modal-title').text(title)
    $("#shareModal").modal('show');
});

$('#invite_send').click(function(event){
    var email = $("#all_mail")
    var to_send_email = email.children()[0].innerText.slice(0,-2)
    var url_to_share = window.location.origin + window.location.pathname
    debugger
    invite_url = window.location.origin + '/hobo_user/user_home/invite/'

    invite_url_args = {
        "to_user_email": to_send_email,
        "project_url": url_to_share,
    }

    token_auth_str = 'Token 44c4706c17c655c1332b513d26c62754e25557d7'
    debugger
    axios.post(invite_url, invite_url_args, {headers: { 'Authorization': token_auth_str }})
    .then((response) => {
        debugger
        console.log(response);
    }, (error) => {
        debugger
        console.log(error);
    });

});

$('#share-close-btn').click(function(event){
    $("#shareModal").modal('hide');
});

$('#share-close-cross').click(function(event){
    $("#shareModal").modal('hide');
});

get_friends_list_url = origin_url + '/payment/paypal/create/'

$('#invite-link').click(function(event){
    var modal = $("#inviteModal")
    var title = "Invite to"
    modal.find('.modal-title').text(title)
    $("#inviteModal").modal('show');

    axios.get(get_friends_list_url)
    .then((response) => {
        plan_id = response.data.plan_id
    }, (error) => {
        console.log(error);
    });

});

$('#shareModalClose').click(function(event){
    $("#shareModal").modal('hide');
});


$('#inviteModalClose').click(function(event){
    $("#inviteModal").modal('hide');
});

$('#cancel_invite_btn').click(function(event){
    $("#inviteModal").modal('hide');
});