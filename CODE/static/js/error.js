document.addEventListener("DOMContentLoaded", function () {
    var messages = document.getElementById('flash-messages').dataset.messages;
    if (messages) {
        alert(messages);
    }
});