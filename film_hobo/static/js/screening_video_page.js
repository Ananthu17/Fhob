$('#share-link').click(function(event){
    var modal = $("#shareModal")
    var title = "Share to"
    modal.find('.modal-title').text(title)
    $("#shareModal").modal('show');
});

$('#share-close-btn').click(function(event){
    $("#shareModal").modal('hide');
});

$('#share-close-cross').click(function(event){
    $("#shareModal").modal('hide');
});

origin_url = window.location.origin
get_friends_list_url = origin_url + '/payment/paypal/create/'

$('#invite-link').click(function(event){
    var modal = $("#inviteModal")
    var title = "Invite to"
    modal.find('.modal-title').text(title)
    $("#inviteModal").modal('show');

    axios.get(get_friends_list_url)
    .then((response) => {
        debugger
        plan_id = response.data.plan_id
    }, (error) => {
        debugger
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