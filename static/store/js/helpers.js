function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// generates uuid4 that will be assigned to device id
function uuidv4() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    var r = (Math.random() * 16) | 0,
      v = c == "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

// gets device from the cookies
let device = getCookie("device");
// generates device id if there is none and adds it to cookies
if (device == null || device == undefined) {
  device = uuidv4();
}
document.cookie = "device=" + device + ";domain=;path=/";

// keep cursor position on page reload

document.addEventListener("DOMContentLoaded", function (event) {
  var scrollpos = sessionStorage.getItem("scrollpos");
  if (scrollpos) {
    window.scrollTo(0, scrollpos);
    sessionStorage.removeItem("scrollpos");
  }
});

window.addEventListener("beforeunload", function (e) {
  sessionStorage.setItem("scrollpos", window.scrollY);
});
