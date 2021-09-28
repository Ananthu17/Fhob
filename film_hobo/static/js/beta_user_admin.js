
/*
get membership fee details and render to html
*/
var token = localStorage.getItem("token");
token_str = "Token "
token_val = String(token)
var authorization_str = token_str.concat(token_val);
origin_url = window.location.origin

/*
get details of new beta user code and pass to add discount api
*/
document.getElementById("beta_user_code_add").addEventListener("click", function() {

  add_url = origin_url + '/hobo_user/add-beta-tester-code/'
  var add_args = {
      "code": document.getElementById("beta_user_code_name_input").value,
      "days": document.getElementById("beta_user_code_days_input").value
  }

  axios.post(add_url, add_args, {headers: { "Authorization": authorization_str}})
  .then((response) => {
      if (response.status == 201){
          $('#beta_user_code_name_input').val('');
          $('#beta_user_code_days_input').val('');
          location.reload();
      }
  }, (error) => {
      console.log(error);
  });

});

get_list_url = origin_url + '/hobo_user/list-beta-tester-code/'

/*
delete code record funtion
*/
function deleteCodeFunction(obj_id) {
  var button_name = '#remove_btn' + obj_id
  var title = $(button_name).attr("data-title")
  var modal = $("#payment_admin_modal")
  var modal_text = "Are you sure you want to delete this code?"
  modal.find('.modal-title').text(title)
  modal.find('.modal-body').text(modal_text)
  $("#modal_delete").attr("value", obj_id)
  $("#payment_admin_modal").modal('show');
}

function editCodeFunction(obj_id) {
  edit_field_element = '#modify_edit_' + obj_id
  edit_state = $(edit_field_element).text()
  if (edit_state === 'Edit'){
      $(edit_field_element).html("Save");

      editable_fields = 'edit' + obj_id
      var editable_elements = document.getElementsByClassName(editable_fields);
      for (var i = 0; i < editable_elements.length; i++) {
          element_to_change = editable_elements
          if (editable_elements.item(i).contentEditable == true) {
              editable_elements.item(i).contentEditable = false;
          } else {
              editable_elements.item(i).contentEditable = true;
          }
      }
  }
  else{
    editable_fields = 'edit' + obj_id
    var editable_elements = document.getElementsByClassName(editable_fields);
    edit_beta_tester_code_url = origin_url + '/hobo_user/edit-beta-tester-code/'

    for (var i = 0; i < editable_elements.length; i++) {
      beta_tester_code_val = editable_elements.item(0).textContent
      amount_val = editable_elements.item(1).textContent
    }
    editable_fields = '.edit' + obj_id
    var edit_class = $(editable_fields);

    beta_tester_code_args = {
      "code": editable_elements[0].innerText,
      "days": editable_elements[1].innerText,
    }

    axios.put(edit_beta_tester_code_url, beta_tester_code_args, {headers: {'Authorization': authorization_str}})
    .then((response) => {
      if (response.status == 200){

      }
    }, (error) => {
      console.log(error);
    });

  }
}

$( document ).ready(function() {
  axios.get(get_list_url, {headers: {'Authorization': authorization_str}})
  .then((response) => {
    beta_tester_objs = response.data

    let table = '<thead> <tr> <th>Beta User Code Name</th> <th>Timeframe</th> <th colspan="2">Action</th> </tr></thead><tbody></tbody>';
      beta_tester_objs.forEach(function(d){
      obj_id = d.id
      delete_url = origin_url + '/hobo_user/delete-beta-tester-code/' + d.id
      table += '<tr><td contenteditable="false" class="edit'+d.id+'">'+d.code+'</td><td contenteditable="false" class="edit'+d.id+'">'+d.days+'</td>';
      table += '<td><a id="remove_btn'+d.id+'" class="modify_remove_id admin-bill-link" data-toggle="modal" data-target="#payment_admin_modal" alt="modify_remove" value="'+d.id+'" href="#" onclick="return deleteCodeFunction('+obj_id+')" data-title="Remove Discount">Remove</a></td></tr>';
    })
    table += '</tbody>';
    $('#beta_user_code_table').empty().html(table);
  });
});

$("#modal_delete").click(function(){
  obj_id = $("#modal_delete").attr("value")
  delete_url = origin_url + '/hobo_user/delete-beta-tester-code/' + obj_id + '/'
  axios.delete(delete_url, {headers: {'Authorization': authorization_str}})
  .then((response) => {
  if (response.status == 200){
          location.reload();
      }
  }, (error) => {
      console.log(error);
  });
});