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
// Listen to the change in radio buttons and hide/show prices accordingly
$("input:radio").change(function () {
  // retrieve id of the checked button
  var checked_size_id = $(this).attr("id");
  // retrieve product number to hide price
  var product_number = checked_size_id.split("-")[1];
  // hide all prices
  $(".prices-" + product_number).hide();
  // use an attribute selector if class contains dot
  if (checked_size_id.includes("")) $(`[class~='${checked_size_id}']`).show();
  else $("." + checked_size_id).show();
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
