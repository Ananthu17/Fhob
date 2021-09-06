    // cancel cast attach request
    $('body').on('click' , '.cancel_cast_request', function(){
        var id = $(this).attr('id');
        var token = $("#token").val();
        var data_dict = {}
        data_dict['type'] = 'cancel';
        if(id){
            data_dict['character_id'] = id;
        }
        console.log(data_dict)
        $.ajax
            ({
                type: "POST",
                url: "/project/cancel-cast-attach-request-api/",
                dataType: 'json',
                async: false,
                data: data_dict,
                beforeSend: function (xhr) {
                    xhr.setRequestHeader ("Authorization", token);
                },
                success: function (response){
                    window.location.reload();
                }
            });
    });
    $('body').on('click' , '.decline_cast_request', function(){
        var character_id = $(this).attr('id');
        var token = $("#token").val();
        var notification_id = "#cast-attach-req-btns-"+character_id
        var data_dict = {}
        data_dict['type'] = 'decline';
        if(character_id){
            data_dict['character_id'] = character_id;
        }
        console.log(data_dict)
        $.ajax
            ({
                type: "POST",
                url: "/project/cancel-cast-attach-request-api/",
                dataType: 'json',
                async: false,
                data: data_dict,
                beforeSend: function (xhr) {
                    xhr.setRequestHeader ("Authorization", token);
                },
                success: function (response){
                    var msg = "Cast attach request from "+response['project']+" removed."
                    $(notification_id).html(" ");
                    $(notification_id).html(msg)
                }
            });
    });

    $('body').on('click' , '.accept_cast_attach_request', function(){
        var character_id = $(this).attr("id");
        var token = $("#token").val();
        var data_dict = {};
        data_dict['character_id'] = character_id;
        var notification_id = "#cast-attach-req-btns-"+character_id
        console.log(data_dict)
        $.ajax
        ({
            type: "POST",
            url: "/project/accept-cast-attach-request-api/",
            dataType: 'json',
            async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function (response){
                var msg = "Congratulations!! You have been attached to project <b>"+response['project']+"</b> as character <b>"+response['character']+"</b>"
                $(notification_id).html(" ");
                $(notification_id).html(msg)
            }
        });
    });