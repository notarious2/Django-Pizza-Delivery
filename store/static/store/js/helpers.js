// AJAX to send post request -> good for implement stuff
// that does not require reload -> in my case I reloaded anyways

// $(document).on("click", ".js-add", function (event) {
//   event.preventDefault();
//   console.log("Clicked!!!");
//   var productID = $(this)
//     .closest(".individual-container")
//     .find(".productID")
//     .val();
//   console.log("product ID:", productID);
//   $.ajax({
//     type: "POST",
//     url: $(this).closest(".individual-container").find("form").attr("action"),
//     success: function () {
//       location.reload();
//     },
//   });
// });
