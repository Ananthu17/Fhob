$(document).ready(function(){
        $.get('/project/show-top-rated-member/')
        .done(function(data) {
            if(data.results!='')
                {
                    $('.top_rated_members').html(" ")
                    $('.top_rated_members').html(data['top_rated_members_html']);
                }
        });
});