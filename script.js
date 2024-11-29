async function fetchTags() {
    const tagsDropdown = document.getElementById("tags");
    try {
        const response = await fetch("http://127.0.0.1:5001/tags");
        const tags = await response.json();
        tags.forEach(tag => {
            const option = document.createElement("option");
            option.value = tag;
            option.textContent = tag;
            tagsDropdown.appendChild(option);
        });
    } catch (error) {
        console.error("Failed to load tags:", error.message);
    }
}

async function sendQuery() {
    const query = document.getElementById("query").value.trim();
    const responseDiv = document.getElementById("response");
    const historyList = document.getElementById("history-list");

    if (!query) {
        responseDiv.textContent = "Please enter a question!";
        return;
    }

    responseDiv.textContent = "Loading...";
    try {
        const response = await fetch("http://127.0.0.1:5001/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: query }),
        });
        const data = await response.json();
        const answer = data.answer || "I'm sorry, I couldn't find an answer to your question.";

        responseDiv.textContent = `Answer: ${answer}`;
        const historyItem = document.createElement("li");
        historyItem.innerHTML = `<b>You:</b> ${query}<br><b>Bot:</b> ${answer}`;
        historyList.appendChild(historyItem);
    } catch (error) {
        responseDiv.textContent = `Error: ${error.message}`;
    }
}

async function sendTagQuery() {
    const tag = document.getElementById("tags").value;
    if (!tag) return;

    const responseDiv = document.getElementById("response");
    const historyList = document.getElementById("history-list");
    responseDiv.textContent = "Loading...";

    try {
        const response = await fetch(`http://127.0.0.1:5001/tag/${tag}`);
        const data = await response.json();
        const answer = data.answer || "No response available for this tag.";

        responseDiv.textContent = `Answer: ${answer}`;
        const historyItem = document.createElement("li");
        historyItem.innerHTML = `<b>You:</b> (Tag: ${tag})<br><b>Bot:</b> ${answer}`;
        historyList.appendChild(historyItem);
    } catch (error) {
        responseDiv.textContent = `Error: ${error.message}`;
    }
}

window.onload = fetchTags;

