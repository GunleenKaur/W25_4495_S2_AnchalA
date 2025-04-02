chrome.runtime.onInstalled.addListener(() => {
    console.log('Spam Detector for Gmail installed.');
    fetchGmailLabels(); // Fetch Gmail labels upon installation
});

// Function to get the access token
function getAccessToken(interactive, callback) {
    console.log("🔍 Starting token retrieval...");
    console.log("🔧 Interactive mode:", interactive);

    chrome.identity.getAuthToken({ interactive: interactive }, (token) => {
        if (chrome.runtime.lastError) {
            console.error("🚫 Error fetching token:", chrome.runtime.lastError);
            callback(null);
            return;
        }

        if (!token) {
            console.warn("⚠️ No token received.");
            callback(null);
            return;
        }

        console.log("✅ Access token retrieved successfully!");

        // Validate token
        fetch(`https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=${token}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("🚫 Invalid or expired token detected.");
                }
                return response.json();
            })
            .then(data => {
                if (!data.scope.includes("https://www.googleapis.com/auth/gmail.readonly")) {
                    console.warn("⚠️ Missing required Gmail scope.");
                }
                callback(token);
            })
            .catch(error => {
                console.error("❌ Token validation failed:", error);
                callback(null);
            });
    });
}

// Listener for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getAccessToken') {
        getAccessToken(request.interactive, (token) => sendResponse({ token }));
        return true; // Asynchronous response
    } else if (request.action === 'fetchEmailContent') {
        getAccessToken(false, (token) => {
            if (token) fetchEmailContent(request.emailId, token, sendResponse);
            else sendResponse({ error: 'Authorization failed.' });
        });
        return true;
    }
});

// Fetch Gmail labels
function fetchGmailLabels() {
    getAccessToken(true, (token) => {
        if (token) {
            fetch('https://www.googleapis.com/gmail/v1/users/me/labels', {
                headers: { Authorization: `Bearer ${token}` }
            })
                .then(response => response.json())
                .then(data => console.log('Labels:', data))
                .catch(error => console.error('Error fetching labels:', error));
        } else {
            console.error('Failed to obtain access token.');
        }
    });
}

function fetchEmailContent(emailId, token, callback) {
    fetch(`https://www.googleapis.com/gmail/v1/users/me/messages/${emailId}`, {
        headers: { Authorization: `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(data => {
        const payload = data.payload;
        let headers = payload.headers;

        // Extract Subject and From from headers
        const subjectHeader = headers.find(header => header.name === "Subject");
        const fromHeader = headers.find(header => header.name === "From");

        const subject = subjectHeader ? subjectHeader.value : "No Subject";
        const from = fromHeader ? fromHeader.value : "Unknown Sender";

        callback({
            emailContent: extractEmailBody(data),
            subject: subject,
            from: from
        });
    })
    .catch(error => {
        console.error('Error fetching email content:', error);
        callback({ error: 'Failed to fetch email content.' });
    });
}

// Extract email body
function extractEmailBody(emailData) {
    const payload = emailData.payload;
    let body = payload.parts ? getHTMLPart(payload.parts) : payload.body.data;
    return decodeURIComponent(escape(atob(body.replace(/-/g, '+').replace(/_/g, '/'))));
}

// Recursive function to get HTML part
function getHTMLPart(parts) {
    for (const part of parts) {
        if (part.mimeType === 'text/html') return part.body.data;
        if (part.parts) return getHTMLPart(part.parts);
    }
    return '';
}

// Function to check if email is already processed and then analyze it
function checkAndProcessEmail(emailId, emailContent, subject, from) {
    fetch('http://localhost:9005/emails/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            emailId: emailId,
            emailText: emailContent
        })
    })
    .then(response => response.json())
    .then((data) => {
        if (data.status === 'processed') {
            console.log('Email already processed:', emailId);
        } else if (data.status === 'stored') {
            console.log('Email is being processed for the first time:', emailId);
            sendEmailContentForAnalysis(emailId, emailContent, subject, from);
        }
    })
    .catch((error) => {
        console.error('❌ Error processing email:', error);
    });
}



// Send email content for spam analysis
function sendEmailContentForAnalysis(emailId, emailContent, subject, from) {
    console.log('🚀 Sending email content for spam analysis:', emailContent);

    fetch('http://127.0.0.1:9005/classify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: emailContent, model: 'naive_bayes' }),
    })
    .then((response) => response.json())
    .then((data) => {
        console.log('✅ Spam analysis result:', data);
        if (data.spam) {
            notifySpamEmail(emailId, subject, from, true);
        } else {
            console.log('Email is not classified as spam.');
//            notifySpamEmail(emailId, subject, from, true);

        }
    })
    .catch((error) => {
        console.error('❌ Error contacting backend:', error);
        showNotification(null, true); // Error notification
    });
}

function showNotification(isSpam, isError = false) {
    let message = isError
        ? "⚠️ Error contacting spam analysis service."
        : isSpam
        ? "🚫 This email is classified as SPAM."
        : "✅ This email is safe.";

    chrome.notifications.create({
        type: "basic",
        iconUrl: "icon.png", // Replace with your icon path
        title: "New Email Detected",
        message: message,
        priority: 2
    });
}


const emailDetails = {};

function notifySpamEmail(emailId, subject, from, isSpam) {
    emailDetails[emailId] = { subject, from, isSpam };
    console.log("📩 Storing email details for ID:", emailId, emailDetails[emailId]);

    chrome.notifications.create(emailId, {
        type: "basic",
        iconUrl: chrome.runtime.getURL("spam.png"),
        title: "Spam Alert",
        message: `Subject: ${subject}\nFrom: ${from}\n${isSpam ? '🚫 Marked as Spam' : '✅ Safe Email'}`,
        priority: 2,
        requireInteraction: true
    }, (notificationId) => {
        if (chrome.runtime.lastError) {
            console.error("❌ Error creating notification:", chrome.runtime.lastError);
        } else {
            console.log("✅ Notification created successfully! ID:", notificationId);
        }
    });
}

function pollEmails(interval = 6000) {
    getAccessToken(true, (token) => {
        if (token) {
            setInterval(() => {
                fetch('https://www.googleapis.com/gmail/v1/users/me/messages?q=is:unread', {
                    headers: { Authorization: `Bearer ${token}` }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.messages) {
                        data.messages.forEach(msg => {
                            fetchEmailContent(msg.id, token, (contentResponse) => {
                                checkAndProcessEmail(msg.id, contentResponse.emailContent, contentResponse.subject, contentResponse.from);
                            });
                        });
                    }
                })
                .catch(error => console.error('Error polling emails:', error));
            }, interval);
        } else {
            console.error('Failed to get access token.');
        }
    });
}

pollEmails();

