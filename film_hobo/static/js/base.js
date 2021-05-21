/*
code to store token info into local storage on login
*/
document.getElementById("login-submit").addEventListener("click", function() {
    var email = $('#id_username').val();
    var password = $('#id_password').val();
    origin_url = window.location.origin
    post_url = origin_url + '/hobo_user/login/'
    extra_args = {"email": email.toString(), "password": password.toString()}
    axios.post(post_url, extra_args)
    .then((response) => {
        localStorage.setItem('token', response.data.key);
    }, (error) => {
        console.log(error);
    });
});

/*
code to clear token info from local storage on logout
*/
document.getElementById("logout_link").addEventListener("click", function() {
    localStorage.removeItem("token");
});
