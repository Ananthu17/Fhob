
    $('body').on('click' , '.track_project', function(){
        var name = $(this).attr("id");
        var token = $("#token").val();
        var msg = "Started Tracking "+name;
        var project_id = $("#project_id").val();
        var data_dict = {}
        data_dict['project_id'] = project_id;
        console.log(data_dict)
        $('.track-btn').html("<a class='mem-blu-link log-fnt-weight cursor-pointer '>U<span class='mem-small-f'>PDATING...</span></a>");
        $.ajax
        ({
            type: "POST",
            url: "/project/track-project-api/",
            dataType: 'json',
            // async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function (response){
                $('.track-btn').html(" ")
                $('#success_message').fadeIn().html(msg);
                setTimeout(function() {$('#success_message').fadeOut("slow");}, 2000 );
                $('.track-btn').html("<a class='mem-blu-link cursor-pointer un_track_project' id='"+name+"'>T<span class='mem-small-f'>RACKING</span></a>");
            }
        });
    });

    $('body').on('click' , '.un_track_project', function(){
        var name = $(this).attr("id");
        var token = $("#token").val();
        var project_id = $("#project_id").val();
        var data_dict = {}
        var msg = "Stopped tracking "+name;
        data_dict['project_id'] = project_id;
        $.ajax
        ({
            type: "POST",
            url: "/project/untrack-project-api/",
            dataType: 'json',
            async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function (response){
                $('#warning_message').fadeIn().html(msg);
				setTimeout(function() {$('#warning_message').fadeOut("slow");}, 2000 );
                $('.track-btn').html(" ")
                $('.track-btn').html("<a class='mem-blu-link log-fnt-weight cursor-pointer track_project' id='"+name+"'>T<span class='mem-small-f'>RACK</span></a>");
            }
        });
    });