
    $('body').on('click' , '.track', function(){
        var name = $(this).attr("id");
        var token = $("#token").val();
        var msg = "Started Tracking "+name;
        var track_id = $("#track_id").val();
        var data_dict = {}
        data_dict['track_id'] = track_id;
        $('.track-btn').html("<a class='mem-blu-link cursor-pointer un_track'>U<span class='mem-small-f'>PDATING...</span></a>");
        $.ajax
        ({
            type: "POST",
            url: "/hobo_user/track-user-api/",
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
                $('.track-btn').html("<a class='mem-blu-link cursor-pointer un_track' id='"+name+"'>T<span class='mem-small-f'>RACKING</span></a>");
            }
        });
    });

    $('body').on('click' , '.un_track', function(){
        var name = $(this).attr("id");
        var token = $("#token").val();
        var track_id = $("#track_id").val();
        var data_dict = {}
        var msg = "Stopped tracking "+name;
        data_dict['track_id'] = track_id;
        $.ajax
        ({
            type: "POST",
            url: "/hobo_user/untrack-user-api/",
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
                $('.track-btn').html("<a class='mem-blu-link cursor-pointer track' id='"+name+"'>T<span class='mem-small-f'>RACK</span></a>");
            }
        });
    });