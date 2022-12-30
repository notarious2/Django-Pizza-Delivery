function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// generates uuid4
function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}


// gets device from the cookies
let device = getCookie('device')
// generates device id if there is none and adds it to cookies
if (device == null || device == undefined){
    device = uuidv4()
}
document.cookie ='device=' + device + ";domain=;path=/"

// keep cursor position on page reload

document.addEventListener("DOMContentLoaded", function (event) {
    var scrollpos = sessionStorage.getItem('scrollpos');
    if (scrollpos) {
        window.scrollTo(0, scrollpos);
        sessionStorage.removeItem('scrollpos');
    }
});

window.addEventListener("beforeunload", function (e) {
    sessionStorage.setItem('scrollpos', window.scrollY);
});

var csrftoken = "{{csrf_token}}";
  $(document).on("click", ".js-add", function () {
    var closestDiv = $(this).closest(".individual-container");
    var size = closestDiv.find("input[name='size']:checked").val();
    var quantity = closestDiv.find("input[name='quantity']").val();
    $.ajax({
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      type: "POST",
      url: $(this).closest(".individual-container").find("form").attr("action"),
      data: JSON.stringify({ size: size, quantity: quantity }),
      success: function (data) {
        $(document).find(".cart-count").text(data.cart_total);
        var popupMessage = closestDiv.find(".product-added");
        popupMessage.show();
        setTimeout(function () {
          popupMessage.hide();
        }, 1000);
        // reset input field
        closestDiv.find("input[name='quantity']").val("1");
      },
    });
  });
  $("input:radio").change(function () {
    // retrieve id of the checked button
    var checked_size_id = $(this).attr("id");
    // retrieve product number to hide price
    var product_number = checked_size_id.split("-")[1];
    $(".prices-" + product_number).hide();
    $("." + checked_size_id).show();
  });

  // incrementing quantity
  $(".increment").click(function () {
    // find closest input
    var closestDiv = $(this).closest(".individual-container");
    var quantityInput = closestDiv.find("input[name='quantity']");
    var inputValue = parseInt(quantityInput.val());
    inputValue++;
    quantityInput.val(inputValue);
  });

  // decrementing quantity
  $(".decrement").click(function () {
    // find closest input
    var closestDiv = $(this).closest(".individual-container");
    var quantityInput = closestDiv.find("input[name='quantity']");
    var inputValue = parseInt(quantityInput.val());
    // only decrement if value is greater than 1
    if ($(quantityInput).val() > 1) {
      inputValue--;
      quantityInput.val(inputValue);
    }
  });