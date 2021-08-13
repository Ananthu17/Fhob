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
            $('.notification-bell').html(
                '<span class="notification_count_span">'+response['unread_count']+'</span>'
                )
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
                            '<span class="notification_count_span">'+response['unread_count']+'</span>'
                            )
                    }
                }
            });
        }
    });
});