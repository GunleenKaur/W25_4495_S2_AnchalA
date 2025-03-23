console.log("Spam Email Detector - Gmail Scanner Loaded");

// Function to scan emails
function scanEmails() {
    let emails = document.querySelectorAll('.zA'); // Gmail email elements 

    emails.forEach(email => {
        let subjectElement = email.querySelector('.bog');
        let snippetElement = email.querySelector('.y2');

        if (subjectElement && snippetElement) {
            let subject = subjectElement.innerText;
            let snippet = snippetElement.innerText;

            // Send email content to the background script for spam detection
            chrome.runtime.sendMessage({ subject: subject, snippet: snippet }, (response) => {
                if (response && response.isSpam) {
                    email.style.backgroundColor = "rgba(255, 0, 0, 0.3)"; // Highlight spam emails in red
                }
            });
        }
    });
}

// MutationObserver to detect new emails
const observer = new MutationObserver(scanEmails);
observer.observe(document.body, { childList: true, subtree: true });

// Run scan on initial page load
scanEmails();
