origin_url = window.location.origin
get_beta_tester_code_id_url = origin_url + "/hobo_user/get-beta-tester-code-id/"

$( document ).ready(function() {
    $("#beta-user-div").hide();
    $("#beta-user-code-div").hide();
    $("#beta-user-code-lastdate-div").hide();
    var betacode = localStorage.getItem("beta-code");
    if (betacode){
        $("#id_beta_user").val("True");
    }

    var get_args = {
        "code": betacode,
    }
    axios.post(get_beta_tester_code_id_url, get_args)
    .then((response) => {
        if (response.status == 200){
            $("#id_beta_user_code").val(response.data.code_id);
            $("#id_beta_user_end").val(response.data.final_day);
        }
    }, (error) => {
        console.log(error);
    });


});