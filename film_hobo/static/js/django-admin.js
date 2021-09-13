/*
code to store token info into local storage on login
*/
email_element = $("[name=username]")
password_element = $("[name=password]")
button_element = $("[value='Log in']")

$("[value='Log in']").click(function(){
    var email = email_element.val();
    var password = password_element.val();
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
$('a:contains("Log out")').click(function(){
    localStorage.removeItem("token");
});