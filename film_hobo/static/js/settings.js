// change password
$('body').on('click' , '#change-password', function(){
    var token = $("#token").val();
    var old_password = $('input[name="old_password"]').val();
    var new_password1 = $('input[name="new_password1"]').val();
    var new_password2 = $('input[name="new_password2"]').val();
    var data_dict = {}

    $('.old_password-error').html(" ")
    $('.new_password1-error').html(" ")
    $('.new_password2-error').html(" ")
    if(old_password){
        data_dict['old_password']=old_password
    }
    else{
        $('.old_password-error').html("This field is required")
    }
    if(new_password1){
        data_dict['new_password1']=new_password1
    }
    else{
        $('.new_password1-error').html("This field is required")
    }
    if(new_password2){
        data_dict['new_password2']=new_password2
    }
    else{
        $('.new_password2-error').html("This field is required")
    }

    if((old_password != '')&(new_password1 != '')&(new_password2 != '')){
        $.ajax
        ({
            type: "POST",
            url: "/hobo_user/change-password-api/",
            dataType: 'json',
            async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            error: function(data){
                response = data['responseText']
                var response_dict = JSON.parse(response);
                $('.old_password-error').html(response_dict['old_password'])
                $('.new_password2-error').html(response_dict['new_password2'])
            },
            success: function(response){
                if(response['status']=='200'){
                    $('.new_password2-error').html("Password Changed")
                    $('input[name="old_password"]').val('')
                    $('input[name="new_password1"]').val('')
                    $('input[name="new_password2"]').val('')
                }else{
                    $('.new_password2-error').html(response['errors'])
                }
            }
        });
    }
});

// disable account
$('body').on('click' , '#disable-my-account', function(){
    var token = $("#token").val();
    var reason = $('input[name="reason"]:checked').val();
    var data_dict = {}
    if(reason){
        data_dict['reason']=reason
        $.ajax
        ({
            type: "POST",
            url: "/hobo_user/disable-account-api/",
            dataType: 'json',
            async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function(response){
                if(response['status']=='200'){
                    window.location.href = "/hobo_user/enable-account";
                }
            }
        });
    }else{
        $('.disable-error').html("Choose one option")
    }
});

// block members dropdown
$(document).ready(function() {
    $('#all_members').select2();
});


// block user tab button
     $('body').on('click' , '#block-user-tab', function(){
        var token = $("#token").val();
        $.ajax
        ({
            type: "GET",
            url: "/hobo_user/block-members-api/",
            dataType: 'json',
            async: false,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function (response){
                blocked_members_dict = response['blocked_members']
                if(jQuery.isEmptyObject(blocked_members_dict)){
                    $("#blocked-list-title").hide();
                    $("#empty-title").show();
                    $("#all_blocked_members").hide();
                    $(".unblock").hide();
                }else{
                $("#empty-title").hide();
                $("#blocked-list-title").show();
                $('#all_blocked_members').empty()
                $('#all_blocked_members').append($("<option></option>")
                .attr("value", " ")
                .text(" "));
                $.each(blocked_members_dict, function( k, v ) {
                    $('#all_blocked_members').append($("<option></option>")
                    .attr("value", k)
                    .text(v));
                });
             }
            }
        });
     });

// block a member
    $('body').on('click' , '#block_user', function(){
        var user_id = $('#all_members').find("option:selected").val();
        var name = $('#all_members').find("option:selected").text();
        var token = $("#token").val();
        var data_dict = {}
        if(user_id){
            data_dict['user_id'] = user_id;
        }
        console.log(data_dict)
        $.ajax
        ({
            type: "POST",
            url: "/hobo_user/block-members-api/",
            dataType: 'json',
            async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function (){
                $("#empty-title").hide();
                $(".unblock").show();
                $("#all_blocked_members").show();
                $("#blocked-list-title").show();

                // get blocked members
                $.ajax
                ({
                    type: "GET",
                    url: "/hobo_user/block-members-api/",
                    dataType: 'json',
                    async: false,
                    beforeSend: function (xhr) {
                        xhr.setRequestHeader ("Authorization", token);
                    },
                    success: function (response){
                        blocked_members_dict = response['blocked_members']
                        if(jQuery.isEmptyObject(blocked_members_dict)){
                            $("#blocked-list-title").hide();
                            $(".unblock").hide();
                            $("#all_blocked_members").hide();
                            $("#empty-title").show();
                        }else{
                            $("#empty-title").hide();
                            $("#blocked-list-title").show();
                            $('#all_blocked_members').empty()
                            $('#all_blocked_members').append($("<option></option>")
                            .attr("value", " ")
                            .text(" "));
                            $.each(blocked_members_dict, function( k, v ) {
                            $('#all_blocked_members').append($("<option></option>")
                            .attr("value", k)
                            .text(v));
                            });
                        }

                    }
                });

                // get unblocked members
                $.get('/hobo_user/get-unblocked-members/')
                .done(function(data) {
                    if(data.results!='')
                        {
                            $('.dropdown-div').html(" ")
                            $('.dropdown-div').html(data['blocked_users_html']);
                        }
                });

            }
        });
    });

    // general settings
    $('body').on('click' , '#edit_first_name', function(){
         $('#first_name').removeAttr("disabled");
         $('#first_name').css({
            'border': '1px solid #c7c7c7'
            });
    });
    $('body').on('click' , '#edit_middle_name', function(){
         $('#middle_name').removeAttr("disabled");
         $('#middle_name').css({
            'border': '1px solid #c7c7c7'
            });
    });
    $('body').on('click' , '#edit_last_name', function(){
         $('#last_name').removeAttr("disabled");
         $('#last_name').css({
            'border': '1px solid #c7c7c7'
            });
    });
    $('body').on('click' , '#edit_email', function(){
         $('#email').removeAttr("disabled");
         $('#email').css({
            'border': '1px solid #c7c7c7'
            });
    });

// unblock a member
    $('body').on('click' , '.unblock', function(){
        var id = $("#all_blocked_members").find("option:selected").val();
        var token = $("#token").val();
        var obj_id = id;
        var data_dict = {}
        data_dict['user_id'] = obj_id;
        $.ajax
        ({
            type: "POST",
            url: "/hobo_user/unblock-members-api/",
            dataType: 'json',
            async: false,
            data: data_dict,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", token);
            },
            success: function (response){
                // get blocked members
                $.ajax
                    ({
                        type: "GET",
                        url: "/hobo_user/block-members-api/",
                        dataType: 'json',
                        async: false,
                        beforeSend: function (xhr) {
                            xhr.setRequestHeader ("Authorization", token);
                        },
                        success: function (response){
                            blocked_members_dict = response['blocked_members']
                            if(jQuery.isEmptyObject(blocked_members_dict)){
                                $("#blocked-list-title").hide();
                                $(".unblock").hide();
                                $("#all_blocked_members").hide();
                                $("#empty-title").show();
                            }else{
                                $("#empty-title").hide();
                                $("#blocked-list-title").show();
                                $('#all_blocked_members').empty()
                                $('#all_blocked_members').append($("<option></option>")
                                .attr("value", " ")
                                .text(" "));
                                $.each(blocked_members_dict, function( k, v ) {
                                $('#all_blocked_members').append($("<option></option>")
                                .attr("value", k)
                                .text(v));
                                });
                            }

                        }
                    });
                    // get unblocked members
                    $.get('/hobo_user/get-unblocked-members/')
                    .done(function(data) {
                        if(data.results!='')
                            {
                                $('.dropdown-div').html(" ")
                                $('.dropdown-div').html(data['blocked_users_html']);
                            }
                    });
            }
        });

    });