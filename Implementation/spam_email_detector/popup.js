document.getElementById("checkSpam").addEventListener("click", async function() {
    let emailText = document.getElementById("email_text").value;

    if (emailText.trim() === "") {
        document.getElementById("result").innerText = "Please enter some text!";
        return;
    }

    let response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email_text: emailText })
    });

    let data = await response.json();
    document.getElementById("result").innerText = data.spam ? "🚨 This is spam!" : "✅ Not spam.";
});
