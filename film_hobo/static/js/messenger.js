 // Add to priority
 $('body').on('click' , '.priority', function(){
    var msg_thread = $(this).attr("id");
    var token = $("#token").val();
    var priority_btn = "#priority_btn_"+msg_thread
    $.ajax
    ({
        type: "POST",
        url: "/message/add-to-priority-api/",
        dataType: 'json',
        async: false,
        data: {"msg_thread":msg_thread},
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", token);
        },
        success: function(response){
            $(priority_btn).html('<a class="remove_from_priority cursor-pointer remove-decoration color-style" id="'+msg_thread+'" style="color:#b5b4b4!important;"><i class="fa fa-star mr-1" aria-hidden="true"></i>Priority </a>')
            $('#success_message').fadeIn().html("Message added to priority list.");
            setTimeout(function() {$('#success_message').fadeOut("slow");}, 2000 );
        }
    });
  });

 //  Remove from priority list
 $('body').on('click' , '.remove_from_priority', function(){
    var msg_thread = $(this).attr("id");
    var token = $("#token").val();
    var priority_btn = "#priority_btn_"+msg_id
    $.ajax
    ({
        type: "POST",
        url: "/message/remove-from-priority-api/",
        dataType: 'json',
        async: false,
        data: {"msg_thread":msg_thread},
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", token);
        },
        success: function(response){
            window.location.reload();
        }
    });
  });

 // Delete Message
 $('body').on('click' , '.delete_msg', function(){
    var msg_thread = $(this).attr("id");
    var token = $("#token").val();

    $.ajax
    ({
        type: "POST",
        url: "/message/delete-message-api/",
        dataType: 'json',
        async: false,
        data: {"msg_thread":msg_thread},
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", token);
        },
        success: function(response){
            window.location.reload();
        }
    });
  });

 // Report Spam
 $('body').on('click' , '.report_spam', function(){
    var msg_id = $(this).attr("id");
    var token = $("#token").val();

    $.ajax
    ({
        type: "POST",
        url: "/message/report-spam-api/",
        dataType: 'json',
        async: false,
        data: {"id":msg_id},
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", token);
        },
        success: function(response){
            window.location.reload();
        }
    });
  });