    // cancel crew attach request
    $('body').on('click' , '.cancel_crew_request', function(){
        var id = $(this).attr('id');
        var token = $("#token").val();
        var data_dict = {}
        data_dict['type'] = 'cancel';
        if(id){
            data_dict['id'] = id;
        }
        $.ajax
            ({
                type: "POST",
                url: "/project/cancel-crew-attach-request-api/",
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
    // decline crew attach request
    $('body').on('click' , '.decline_crew_request', function(e){
        var crew_id = $(this).attr('id');
        var token = $("#token").val();
        var notification_id = "#crew-attach-req-btns-"+crew_id
        var data_dict = {}
        e.stopPropagation();
        if(crew_id){
            data_dict['id'] = crew_id;
        }
        console.log(data_dict)
        $.ajax
            ({
                type: "POST",
                url: "/project/decline-crew-attach-request-api/",
                dataType: 'json',
                async: false,
                data: data_dict,
                beforeSend: function (xhr) {
                    xhr.setRequestHeader ("Authorization", token);
                },
                success: function (response){
                    var msg = "Crew attach request from "+response['project']+" removed."
                    $(notification_id).html(" ");
                    $(notification_id).html(msg)
                }
            });
    });

    // accept crew attach request
    $('body').on('click' , '.accept_crew_attach_request', function(e){
        var crew_id = $(this).attr("id");
        var token = $("#token").val();
        var data_dict = {};
        data_dict['id'] = crew_id;
        var notification_id = "#crew-attach-req-btns-"+crew_id
        console.log(data_dict)
        e.stopPropagation();
        $.ajax
        ({
            type: "POST",
            url: "/project/accept-crew-attach-request-api/",
            dataType: 'json',
            async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function (response){
                var msg = "Congratulations!! You have been attached to project <b>"+response['project']+"</b> as <b>"+response['crew']+"</b>"
                $(notification_id).html(" ");
                $(notification_id).html(msg)
            }
        });
    });