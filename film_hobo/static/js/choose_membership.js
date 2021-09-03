var token = localStorage.getItem("token");
token_str = "Token "
token_val = String(token)
var authorization_str = token_str.concat(token_val);
origin_url = window.location.origin

$( document ).ready(function() {
    origin_url = window.location.origin
    get_url = origin_url + '/payment/get_membership_fee_detail_public/'

    axios.get(get_url)
    .then((response) => {
        $('#annual_indie').text(response.data.annual_indie);
        $('#monthly_indie').text(response.data.monthly_indie);
        $('#annual_pro').text(response.data.annual_pro);
        $('#monthly_pro').text(response.data.monthly_pro);
        $('#annual_company').text(response.data.annual_company);
        $('#monthly_company').text(response.data.monthly_company);
    });

    // var modal = $("#membershipModal")
    // var title = "Enter Code"
    // var modal_text = "Enter a Beta Tester Code"
    // modal.find('.modal-title').text(title)
    // modal.find('.modal-body').text(modal_text)
    // $("#membershipModal").modal('show');

});

function withJquery(){
    var temp = $("<input>");
    $("body").append(temp);
    temp.val($('#copyText1').text()).select();
    document.execCommand("copy");
    temp.remove();
    CopyToClipboard($('#copyText1').text(), true, "Value Copied");
}

function CopyToClipboard(value, showNotification, notificationText) {
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val(value).select();
    document.execCommand("copy");
    $temp.remove();

    if (typeof showNotification === 'undefined') {
        showNotification = true;
    }
    if (typeof notificationText === 'undefined') {
        notificationText = "Copied to clipboard";
    }

    var notificationTag = $("div.copy-notification");
    if (showNotification && notificationTag.length == 0) {
        notificationTag = $("<div/>", { "class": "copy-notification", text: notificationText });
        $("body").append(notificationTag);

        notificationTag.fadeIn("slow", function () {
            setTimeout(function () {
                notificationTag.fadeOut("slow", function () {
                    notificationTag.remove();
                });
            }, 1000);
        });
    }
}

$('#close-membership-btn').click(function(event){
    $("#membershipModal").modal('hide');
});

$('#close-cross').click(function(event){
    $("#membershipModal").modal('hide');
});

$('#beta-tester-modal').click(function(event){
    var modal = $("#membershipModal")
    var title = "Enter Code"
    modal.find('.modal-title').text(title)
    $("#membershipModal").modal('show');
});

$('#check-code').click(function(event){
    check_url = origin_url + '/hobo_user/check-beta-tester-code/'
    var check_args = {
        "code": $('#input_code').val(),
    }

    axios.post(check_url, check_args)
    .then((response) => {

    if (response.status == 200){
            var modal = $("#membershipModal")
            var modal_text = "Code Applied Successfully"
            modal.find('.modal-body').text(modal_text)
        }
    }, (error) => {
        console.log(error);
    });
});