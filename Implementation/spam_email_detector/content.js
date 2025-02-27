console.log("Spam Email Detector Content Script Loaded");

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "scanEmail") {
        let emailBody = document.querySelector(".ii.gt").innerText;  // Gmail body selector
        sendResponse({ emailText: emailBody });
    }
});
