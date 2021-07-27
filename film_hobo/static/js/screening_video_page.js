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

$('#invite-link').click(function(event){
    var modal = $("#inviteModal")
    var title = "Invite to"
    modal.find('.modal-title').text(title)
    $("#inviteModal").modal('show');
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