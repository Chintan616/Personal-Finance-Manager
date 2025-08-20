document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        let messageContainer = document.querySelector(".message-container");
        if (messageContainer) {
            messageContainer.style.transition = "opacity 0.5s ease-out";
            messageContainer.style.opacity = "0";

            // Remove message container from the DOM after fading out
            setTimeout(() => {
                messageContainer.remove();
            }, 500);
        }
    }, 1000);
});

document.addEventListener("DOMContentLoaded", function() {
    const messageContainer = document.querySelector(".message-container");
    if (messageContainer) {
        messageContainer.classList.add("show");
    }
});