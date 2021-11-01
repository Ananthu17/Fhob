// cast samr

    $("input[name=cast_samr]:radio").change(function () {
        var cast_samr = $(this).val();
        if(cast_samr=='indie'){
            $('input[name=indie_and_pro_samr_rate]').prop('checked', false);
            $('input[name=indie_samr_rate]').prop('checked', true);
            $('input[name=pro_samr_rate]').prop('checked', false);
        }
        if(cast_samr=='pro'){
            $('input[name=indie_and_pro_samr_rate]').prop('checked', false);
            $('input[name=indie_samr_rate]').prop('checked', false);
            $('input[name=pro_samr_rate]').prop('checked', true);
        }
        if(cast_samr=='indie_and_pro'){
            $('input[name=indie_and_pro_samr_rate]').prop('checked', true);
            $('input[name=indie_samr_rate]').prop('checked', false);
            $('input[name=pro_samr_rate]').prop('checked', false);
        }
    });
    $("input[name=indie_and_pro_samr_rate]:radio").change(function () {
        $('input[name=indie_samr_rate]').prop('checked', false);
        $('input[name=pro_samr_rate]').prop('checked', false);
        $('input[name=cast_samr][value=pro]').prop('checked', false);
        $('input[name=cast_samr][value=indie]').prop('checked', false);
        $('input[name=cast_samr][value=indie_and_pro]').prop('checked', true);
    });
    $("input[name=indie_samr_rate]:radio").change(function () {
        $('input[name=indie_and_pro_samr_rate]').prop('checked', false);
        $('input[name=pro_samr_rate]').prop('checked', false);
        $('input[name=cast_samr][value=pro]').prop('checked', false);
        $('input[name=cast_samr][value=indie]').prop('checked', true);
        $('input[name=cast_samr][value=indie_and_pro]').prop('checked', false);
    });
    $("input[name=pro_samr_rate]:radio").change(function () {
        $('input[name=indie_and_pro_samr_rate]').prop('checked', false);
        $('input[name=indie_samr_rate]').prop('checked', false);
        $('input[name=cast_samr][value=pro]').prop('checked', true);
        $('input[name=cast_samr][value=indie]').prop('checked', false);
        $('input[name=cast_samr][value=indie_and_pro]').prop('checked', false);
    });


// crew samr

    $("input[name=crew_samr]:radio").change(function () {
        var crew_samr = $(this).val();
        if(crew_samr=='indie'){
            $('input[name=crew_indie_and_pro_samr_rate]').prop('checked', false);
            $('input[name=crew_indie_samr_rate]').prop('checked', true);
            $('input[name=crew_pro_samr_rate]').prop('checked', false);
        }
        if(crew_samr=='pro'){
            $('input[name=crew_indie_and_pro_samr_rate]').prop('checked', false);
            $('input[name=crew_indie_samr_rate]').prop('checked', false);
            $('input[name=crew_pro_samr_rate]').prop('checked', true);
        }
        if(crew_samr=='indie_and_pro'){
            $('input[name=crew_indie_and_pro_samr_rate]').prop('checked', true);
            $('input[name=crew_indie_samr_rate]').prop('checked', false);
            $('input[name=crew_pro_samr_rate]').prop('checked', false);
        }
    });
    $("input[name=crew_indie_and_pro_samr_rate]:radio").change(function () {
        $('input[name=crew_indie_samr_rate]').prop('checked', false);
        $('input[name=crew_pro_samr_rate]').prop('checked', false);
        $('input[name=crew_samr][value=pro]').prop('checked', false);
        $('input[name=crew_samr][value=indie]').prop('checked', false);
        $('input[name=crew_samr][value=indie_and_pro]').prop('checked', true);
    });
    $("input[name=crew_indie_samr_rate]:radio").change(function () {
        $('input[name=crew_indie_and_pro_samr_rate]').prop('checked', false);
        $('input[name=crew_pro_samr_rate]').prop('checked', false);
        $('input[name=crew_samr][value=pro]').prop('checked', false);
        $('input[name=crew_samr][value=indie]').prop('checked', true);
        $('input[name=crew_samr][value=indie_and_pro]').prop('checked', false);
    });
    $("input[name=crew_pro_samr_rate]:radio").change(function () {
        $('input[name=crew_indie_and_pro_samr_rate]').prop('checked', false);
        $('input[name=crew_indie_samr_rate]').prop('checked', false);
        $('input[name=crew_samr][value=pro]').prop('checked', true);
        $('input[name=crew_samr][value=indie]').prop('checked', false);
        $('input[name=crew_samr][value=indie_and_pro]').prop('checked', false);
    });



//  script radio button
$('.script_visibility').on('click', function(e) {
    if (radioState === this) {
        this.checked = false;
        radioState = null;
    } else {
        radioState = this;
    }
});