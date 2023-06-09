// creating socket for sending notificaton
var room_name = $("#current_user").val();
if(room_name){
var connectionString = 'ws://' + window.location.host+'/ws/notification/'+room_name + '/';
var notificationSocket = new WebSocket(connectionString);



// when notification is received
notificationSocket.onmessage = function (e) {
    // On getting the message from the server
    // Do the appropriate steps on each event.
    console.log("-----Notification Received----")
    var token = $("#token").val();
    $.ajax
    ({
        type: "GET",
        url: "/hobo_user/get-notification-api/",
        dataType: 'json',
        async: false,
        data: {},
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", token);
        },
        error: function(data){},
        success: function(response){
            console.log("response['unread_count']", response['unread_count'])
            if(response['unread_count']!=0){
                    $('.notification-bell').html(
                        '<span class="mm-icon-button__badge">'+response['unread_count']+'</span>'
                        )
                }
            }
    });
    $.ajax
    ({
        type: "GET",
        url: "/message/get-message-notification-api/",
        dataType: 'json',
        async: false,
        data: {},
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", token);
        },
        error: function(data){},
        success: function(response){
            if(response['unread_msg_count']!=0){
                console.log("count: ",response['unread_msg_count'])
                    $('.message-notification').html(
                        '<span class="mm-icon-button__badge">'+response['unread_msg_count']+'</span>'
                        );
                    $('.message_count').html("("+response['unread_msg_count']+")");
                }
        }
    });
    let data = JSON.parse(e.data);
    // console.log(data)
    var message = data["message"];
    var user_id = data['user_id'];
    var event = data['event'];
    var origin   = window.location.origin
    switch (event) {
        case "TRACK":
             // get tracking notification html
             data_dict = {}
             data_dict['from_user'] = user_id
             $.get('/hobo_user/get-tracking-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['tracking_notification_html'])
                     }
             });
            break;
        case "FRIEND_REQUEST":
             // get friend request notification html
             data_dict = {}
             data_dict['from_user'] = user_id
             $.get('/hobo_user/get-friendrequest-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
             break;
        case "CAST_ATTACH_REQUEST":
            // get friend request notification html
            data_dict = {}
            data_dict['from_user'] = user_id
            $.get('/project/get-cast-attach-request-notification-html/', data_dict)
            .done(function(data) {
                if(data.results!='')
                    {
                        $('.notification-modal-content').prepend(data['notification_html'])
                    }
            });
            break;
        case "CREW_ATTACH_REQUEST":
            // get friend request notification html
            data_dict = {}
            data_dict['from_user'] = user_id
            $.get('/project/get-crew-attach-request-notification-html/', data_dict)
            .done(function(data) {
                if(data.results!='')
                    {
                        $('.notification-modal-content').prepend(data['notification_html'])
                    }
            });
            break;
        case "FRIEND_REQUEST_ACCEPT":
             // get friend request accept notification html
             data_dict = {}
             data_dict['from_user'] = user_id
             $.get('/hobo_user/get-friendrequest-accept-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "USER_RATING":
             // get profile rating notification html
             data_dict = {}
             data_dict['from_user'] = user_id
             data_dict['message'] = message
             console.log(data_dict)
             $.get('/hobo_user/get-profile-rating-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "MEMBERSHIP_CHANGE":
             // get membership change notification html
             data_dict = {}
             data_dict['message'] = message
             console.log(data_dict)
             $.get('/project/get-membership-change-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "INVITE":
            // get invite to see a project notification html
            data_dict = {}
            data_dict['from_user'] = user_id
            data_dict['message'] = message
            console.log(data_dict)
            $.get('/hobo_user/get-profile-rating-notification-html/', data_dict)
            .done(function(data) {
                if(data.results!='')
                    {
                        $('.notification-modal-content').prepend(data['notification_html'])
                    }
            });
            break;
        case "PROJECT_TRACKING":
             // get membership change notification html
             data_dict = {}
             data_dict['message'] = message
             console.log(data_dict)
             $.get('/project/get-project-tracking-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "AUDITION_STATUS":
             // get membership change notification html
             data_dict = {}
             data_dict['message'] = message
             console.log(data_dict)
             $.get('/project/get-audition-status-notification/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "VIDEO_RATING":
             // get membership change notification html
             data_dict = {}
             data_dict['message'] = message
             console.log(data_dict)
             $.get('/project/get-video-rating-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "PROJECT_RATING":
             // get membership change notification html
             data_dict = {}
             data_dict['message'] = message
             console.log(data_dict)
             $.get('/project/get-project-rating-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "COMMENTS_MENTION":
             // get membership change notification html
             data_dict = {}
             data_dict['message'] = message
             console.log(data_dict)
             $.get('/project/get-comments-mention-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "COMMENTS":
             // get membership change notification html
             data_dict = {}
             data_dict['message'] = message
             console.log(data_dict)
             $.get('/project/get-comments-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "COMMENTS_REPLY":
             // get membership change notification html
             data_dict = {}
             data_dict['message'] = message
             console.log(data_dict)
             $.get('/project/get-comments-reply-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "CAST_ATTACH_RESPONSE":
             // get membership change notification html
             data_dict = {}
             data_dict['message'] = message
             console.log(data_dict)
             $.get('/project/get-cast-attach-response-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "CREW_ATTACH_RESPONSE":
             // get membership change notification html
             data_dict = {}
             data_dict['message'] = message
             console.log(data_dict)
             $.get('/project/get-crew-attach-response-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "USER_INTEREST":
             // get membership change notification html
             data_dict = {}
             data_dict['message'] = message
             console.log(data_dict)
             $.get('/project/get-user-interest-notification-html/', data_dict)
             .done(function(data) {
                 if(data.results!='')
                     {
                         $('.notification-modal-content').prepend(data['notification_html'])
                     }
             });
            break;
        case "USER_MESSAGES":
             // get membership change notification html
             data_dict = {}
             data_dict['message'] = message
             data_dict['msg_thread'] = data['msg_thread']
             var chat_box_id = "#new_message_"+data['msg_thread']
             console.log(data_dict)
             $.get('/message/get-new-message-html/', data_dict)
             .done(function(data) {
                 console.log(chat_box_id)
                 if(data.results!='')
                     {
                         $(chat_box_id).prepend(data['new_message_html'])
                     }
             });
            break;
        default:
            console.log("No event")
    }
};

}

// Notification bell icon click
$('body').on('click' , '.notification_icon', function(){
    $.get('/hobo_user/get-all-notification-html/')
    .done(function(data) {
        if(data.results!='')
            {
                $('.notification-modal-content').html("")
                $('.notification-modal-content').html(data['all_notification_html'])
            }
    });
});

// Notification read status change
$('body').on('click' , '.notification_link', function(){
    console.log("click")
    var id = $(this).attr('id')
    var token = $("#token").val();
    data_dict = {
        "id":id,
        "status_type":"read"
     }
     $("#notificationModal").modal('hide');
    $.ajax
    ({
        type: "POST",
        url: "/hobo_user/change-notification-status-api/",
        dataType: 'json',
        async: false,
        data: data_dict,
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", token);
        },
        error: function(data){},
        success: function(response){
            console.log("read ",id)
            $.ajax
            ({
                type: "GET",
                url: "/hobo_user/get-notification-api/",
                dataType: 'json',
                async: false,
                data: {},
                beforeSend: function (xhr) {
                    xhr.setRequestHeader ("Authorization", token);
                },
                error: function(data){},
                success: function(response){
                    console.log("unread_count", response['unread_count'])
                    $('.notification-bell').html("");
                    if(response['unread_count']!=0){
                        $('.notification-bell').html(
                            '<span class="mm-icon-button__badge">'+response['unread_count']+'</span>'
                            )
                    }
                }
            });
        }
    });
});
