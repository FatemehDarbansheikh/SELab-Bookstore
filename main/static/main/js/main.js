document.addEventListener("DOMContentLoaded", function () {
    console.log("CHATBOT JS LOADED");

    const toggleBtn = document.getElementById("chatbot-toggle");
    const chatbotBox = document.getElementById("chatbot-box");
    const closeBtn = document.getElementById("chatbot-close");
    const form = document.getElementById("chatbot-form");
    const input = document.getElementById("chatbot-input");
    const messages = document.getElementById("chatbot-messages");

    if (!toggleBtn || !chatbotBox) {
        console.error("Chatbot elements not found");
        return;
    }

    toggleBtn.addEventListener("click", () => {
        chatbotBox.classList.toggle("hidden");
    });

    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            chatbotBox.classList.add("hidden");
        });
    }

    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const text = input.value.trim();
        if (!text) return;


        messages.innerHTML += `<div class="user-message">${text}</div>`;
        input.value = "";
        messages.scrollTop = messages.scrollHeight;

        const loadingDiv = document.createElement("div");
        loadingDiv.className = "bot-message";
        loadingDiv.innerText = "در حال پردازش...";
        messages.appendChild(loadingDiv);
        messages.scrollTop = messages.scrollHeight;

        try {
            const response = await fetch("/chatbot/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ message: text }),
            });

            const data = await response.json();
            loadingDiv.remove();

            messages.innerHTML += `<div class="bot-message">
                ${data.reply}
            </div>`;
            messages.scrollTop = messages.scrollHeight;

        } catch (error) {
            loadingDiv.remove();
            messages.innerHTML += `<div class="bot-message">
                خطا در ارتباط با سرور
            </div>`;
        }
    });
});


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



window.addEventListener("load", () => {
    const loader = document.getElementById("page-loader");
    if (!loader) return;

    setTimeout(() => {
        loader.style.opacity = "0";
        loader.style.transition = "opacity 0.4s ease";

        setTimeout(() => {
            loader.remove();
        }, 400);
    }, 1500);
});


