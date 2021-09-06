$( document ).ready(function() {
    // $("#beta-user-div").hide();
    var betacode = localStorage.getItem("beta-code");
    if (betacode){
        $("#beta-user-input").val(betacode);
    }
});