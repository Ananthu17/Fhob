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
});