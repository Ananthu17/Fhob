origin_url = window.location.origin

$('#share-link').click(function (event) {
    var modal = $("#shareModal")
    var title = "Share with Friends"
    modal.find('.modal-title').text(title)
    $("#shareModal").modal('show');
});

var token = $("#token")
var token_auth_str = token.val()
var validUsers = [];
var validEmails = [];

get_friends_list_url = origin_url + '/hobo_user/list-all-friend-api/'
axios.get(get_friends_list_url, { headers: { 'Authorization': token_auth_str } })
    .then((response) => {
        var friends_obj = response.data.friends

        $.each(friends_obj, function (key_1, valueObj_1) {
            $.each(valueObj_1, function (key_2, valueObj_2) {
                if (key_2 === "user") {
                    validUsers.push(valueObj_2);
                }
                if (key_2 === "email") {
                    validEmails.push(valueObj_2);
                }
            });
        });

        previousValue = "";

        $('#enter_email').autocomplete({
            source: validUsers
        }).keyup(function () {
            var isValid = false;
            for (i in validUsers) {
                if (validUsers[i].toLowerCase().match(this.value.toLowerCase())) {
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

$('#invite_send').click(function (event) {

    var email = $("#all_mail")
    var email_list = validEmails

    console.log(email_list)
    for (var i = 0, l = email_list.length; i < l; i++) {
        var url_to_share = window.location.origin + window.location.pathname

        invite_url = window.location.origin + '/hobo_user/user_home/invite/'
        invite_url_args = {
            "to_user_email": email_list[i],
            "project_url": url_to_share,
        }

        axios.post(invite_url, invite_url_args, { headers: { 'Authorization': token_auth_str } })
            .then((response) => {
                console.log(response);
                $("#shareModal").modal('hide');
            }, (error) => {
                console.log(error);
                $("#shareModal").modal('hide');
            });
    }
});


$('#url_send').click(function (event) {
    var selectedUsers = $('#userSelect').val();
    var url_to_share = window.location.origin + window.location.pathname
    user_url = window.location.origin + '/hobo_user/user_home/send_url/'
    user_url_args = {
        "selectedUsers": selectedUsers,
        "project_url": url_to_share,
        "url_type": "PROJECT"
    }

    axios.post(user_url, user_url_args, { headers: { 'Authorization': token_auth_str } })
        .then((response) => {
            console.log(response);
            $("#shareModal").modal('hide');
        }, (error) => {
            console.log(error);
            $("#shareModal").modal('hide');
        });
});




$('#profile_url_send').click(function (event) {
    var selectedUsers = $('#userSelect').val();
    var url_to_share = window.location.origin + window.location.pathname
    user_url = window.location.origin + '/hobo_user/user_home/send_url/'
    user_url_args = {
        "selectedUsers": selectedUsers,
        "project_url": url_to_share,
        "url_type": "PROFILE"
    }

    axios.post(user_url, user_url_args, { headers: { 'Authorization': token_auth_str } })
        .then((response) => {
            console.log(response);
            $("#shareModal").modal('hide');
        }, (error) => {
            console.log(error);
            $("#shareModal").modal('hide');
        });
});


$('#cancel_url').click(function (event) {
    alert("ggggggggggggggggggg")
    console.log(response);
    $("#shareModal").modal('hide');
}, (error) => {
    console.log(error);
    $("#shareModal").modal('hide');
});




$('#share-close-btn').click(function (event) {
    $("#shareModal").modal('hide');
});

$('#share-close-cross').click(function (event) {
    $("#shareModal").modal('hide');
});

$('#shareModalClose').click(function (event) {
    $("#shareModal").modal('hide');
});

$('#inviteModalClose').click(function (event) {
    $("#inviteModal").modal('hide');
});

$('#cancel_invite_btn').click(function (event) {
    $("#inviteModal").modal('hide');
});