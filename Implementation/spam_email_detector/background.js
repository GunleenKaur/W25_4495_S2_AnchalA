chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    fetch("http://127.0.0.1:5000/predict", { // Replace with your actual API URL
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject: request.subject, snippet: request.snippet })
    })
    .then(response => response.json())
    .then(data => sendResponse({ isSpam: data.is_spam }))
    .catch(error => console.error("Error:", error));

    return true; // Keeps the message channel open for asynchronous response
});

