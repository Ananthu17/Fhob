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
$('body').on('click' , '.delete_friend_request', function(){
    var token = $("#token").val();
    var id = $(this).attr('id');
    var data_dict = {}
    if(id){
        data_dict['requested_by'] = id;
    }
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
                $(".friend-req-btns").html(" ")
                $(".friend-req-btns").html("Friend request removed.")
            }
        });
});

// Accept friend request
$('body').on('click' , '.accept_friend_request', function(){
    var token = $("#token").val();
    console.log("here=---------")
    var id = $(this).attr('id');
    var data_dict = {}
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
              $(".friend-req-btns").html(" ")
              $(".friend-req-btns").html(msg)
            //   $.get('/hobo_user/update-friend-status/',{'profile_id':id})
            //   .done(function(data) {
            //       if(data.results!='')
            //           {
            //               $('.friend-status').html("")
            //               $('.friend-status').html(data['friend_status_html'])
            //           }
            //   });
            }
        });
});
