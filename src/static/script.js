const chatBody = document.getElementById("chat-body");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

// Simple user ID for this session (replace with more robust method if needed)
const userId = "web_user_" + Date.now();

// Function to add a message to the chat body
function addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
    messageDiv.textContent = text;
    chatBody.appendChild(messageDiv);
    // Scroll to the bottom
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Function to handle sending a message
async function sendMessage() {
    const messageText = userInput.value.trim();
    if (messageText === "") return;

    // Display user message
    addMessage(messageText, "user");

    // Clear input field
    userInput.value = "";
    sendButton.disabled = true; // Disable button while waiting for response

    try {
        const response = await fetch("/api/chat/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ 
                user_id: userId, 
                message: messageText 
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const botResponse = data.response;

        // Display bot response
        addMessage(botResponse, "bot");

    } catch (error) {
        console.error("Error sending message:", error);
        addMessage("Desculpe, ocorreu um erro ao processar a sua mensagem.", "bot");
    } finally {
        sendButton.disabled = false; // Re-enable button
        userInput.focus(); // Focus back on input
    }
}

// Event listeners
sendButton.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

// Initial focus on input
userInput.focus();

