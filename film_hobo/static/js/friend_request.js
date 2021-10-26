// send friend request
$('body').on('click' , '#send_friend_request', function(){
    var token = $("#token").val();
    var profile_user = $("#profile_user").val();
    var data_dict = {}
    if(profile_user){
        data_dict['user'] = profile_user;
    }
    $('.friend_request').html(" ");
    $('.friend_request').html("<span class='red-f bold'>Sending...</span>");
    $.ajax
        ({
            type: "POST",
            url: "/hobo_user/send-friend-request-api/",
            dataType: 'json',
            // async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function (response){
                $('#success_message').fadeIn().html("Friend Request Send");
				setTimeout(function() {$('#success_message').fadeOut("slow");}, 2000 );
                $('.friend_request').html(" ");
                $('.friend_request').html("<span class='red-f bold cursor-pointer' id='cancel_friend_request'>Cancel Friend Request</span>");
            }
        });
});

// unfriend a user
$('body').on('click' , '.unfriend', function(){
    var token = $("#token").val();
    var name = $(this).attr('id');
    var profile_user = $("#profile_user").val();
    var data_dict = {}
    if(profile_user){
        data_dict['user'] = profile_user;
    }
    console.log(data_dict)
    $.ajax
        ({
            type: "POST",
            url: "/hobo_user/unfriend-user-api/",
            dataType: 'json',
            async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function (response){
                var msg = "UnFriend "+name
                $('#warning_message').fadeIn().html(msg);
				setTimeout(function() {$('#warning_message').fadeOut("slow");}, 2000 );
                $('.friend_request').html(" ");
                $('.friend_request').html("<span class='red-f bold cursor-pointer' id='send_friend_request'>Friend Request</span>");
            }
        });
});

// cancel friend request
$('body').on('click' , '#cancel_friend_request', function(){
    var token = $("#token").val();
    var profile_user = $("#profile_user").val();
    var data_dict = {}
    if(profile_user){
        data_dict['user'] = profile_user;
    }
    $.ajax
        ({
            type: "POST",
            url: "/hobo_user/cancel-friend-request-api/",
            dataType: 'json',
            async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function (response){
                $('#warning_message').fadeIn().html("Friend Request Cancelled !!");
				setTimeout(function() {$('#warning_message').fadeOut("slow");}, 2000 );
                $('.friend_request').html(" ");
                $('.friend_request').html("<span class='red-f bold cursor-pointer' id='send_friend_request'>Friend Request</span>");
            }
        });
});

// Delete friend request
$('body').on('click' , '.delete_friend_request', function(e){
    var token = $("#token").val();
    var id = $(this).attr('id');
    var data_dict = {}
    e.stopPropagation();
    if(id){
        data_dict['requested_by'] = id;
    }
    var notification_id = "#friend-req-btns-"+id
    var notification_id_2 = "#friend-request-"+id
    var req_btns = "#btns-"+id
    $.ajax
        ({
            type: "POST",
            url: "/hobo_user/delete-friend-request-api/",
            dataType: 'json',
            async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function (response){
                $(notification_id).html(" ");
                $(notification_id).html("Friend request removed.");
                $(notification_id_2).html(" ");
                $(notification_id_2).html("Friend request removed.");
                $(req_btns).hide();
            }
        });
});

// Accept friend request
$('body').on('click' , '.accept_friend_request', function(e){
    var token = $("#token").val();
    var id = $(this).attr('id');
    var data_dict = {}
    var notification_id = "#friend-req-btns-"+id
    var notification_id_2 = "#friend-request-"+id
    var req_btns = "#btns-"+id
    e.stopPropagation();
    if(id){
        data_dict['requested_by'] = id;
    }
    $.ajax
        ({
            type: "POST",
            url: "/hobo_user/accept-friend-request-api/",
            dataType: 'json',
            async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function (response){
              var msg = "You and "+response['name']+" are now friends."
              $(notification_id).html(" ");
              $(notification_id).html(msg)
              $(notification_id_2).html("");
              $(notification_id_2).append(msg);
              $(req_btns).hide();
            }
        });
});
