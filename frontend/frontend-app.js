function askAI() {
    const question = document.getElementById("question").value;
    const responseBox = document.getElementById("response");

    responseBox.innerText = "Thinking..."; // Show loading state

    fetch("http://127.0.0.1:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
    })
    .then(res => {
        // Handle non-200 status codes (e.g., 400 or 500 errors)
        if (!res.ok) {
            return res.json().then(err => { throw new Error(err.error || `HTTP Error: ${res.status}`); });
        }
        return res.json();
    })
    .then(data => {
        responseBox.innerText = data.response;
    })
    .catch(error => {
        // Handle network errors or errors thrown from the response check
        responseBox.innerText = `Error: ${error.message}. Please check if the backend server is running and your API key is correct.`;
        console.error("API Error:", error);
    });
}

function uploadDocument() {
    const fileInput = document.getElementById("fileInput");
    const responseBox = document.getElementById("response");
    const file = fileInput.files[0];

    if (!file) {
        responseBox.innerText = "Error: Please select a file first.";
        return;
    }

    responseBox.innerText = "Uploading and analyzing document..."; // Show loading state

    const formData = new FormData();
    formData.append("file", file);

    fetch("http://127.0.0.1:5000/analyze-document", {
        method: "POST",
        body: formData
    })
    .then(res => {
        // Handle non-200 status codes
        if (!res.ok) {
            return res.json().then(err => { throw new Error(err.error || `HTTP Error: ${res.status}`); });
        }
        return res.json();
    })
    .then(data => {
        responseBox.innerText = data.response;
    })
    .catch(error => {
        // Handle network errors or thrown errors
        responseBox.innerText = `Error analyzing document: ${error.message}`;
        console.error("Document Analysis Error:", error);
    });
}

// UPDATED: fetchPakistanNews now uses real, verifiable external links
function fetchPakistanNews() {
    const newsContainer = document.getElementById("news-container");
    newsContainer.innerHTML = '<p class="loading-message">Fetching headlines...</p>';

    // Placeholder logic:
    setTimeout(() => {
        // Links updated to real, verifiable articles/pages to ensure they don't redirect
        const dummyNews = [
            { 
                title: "Supreme Court of Pakistan (Legal Context)", 
                source: "Wikipedia", 
                date: "Nov 25, 2025", 
                url: "https://en.wikipedia.org/wiki/Supreme_Court_of_Pakistan" // Verifiable URL
            },
            { 
                title: "Pakistan's Economy and Planning Commission", 
                source: "Wikipedia", 
                date: "Nov 24, 2025", 
                url: "https://en.wikipedia.org/wiki/Planning_Commission_of_Pakistan" // Verifiable URL
            },
            { 
                title: "Digital Laws and Policy in Pakistan", 
                source: "Digital Rights Foundation", 
                date: "Nov 23, 2025", 
                url: "https://digitalrightsfoundation.pk/our-work/" // Verifiable URL
            }
        ];

        let html = '';
        dummyNews.forEach(item => {
            // Wrapping the news-card content in an anchor tag <a> with target="_blank"
            html += `
                <a href="${item.url}" target="_blank" class="news-link"> 
                    <div class="news-card">
                        <h4>${item.title}</h4>
                        <p>Source: ${item.source} | Date: ${item.date}</p>
                    </div>
                </a>
            `;
        });
        newsContainer.innerHTML = html;
        document.getElementById("response").innerText = "News headlines updated successfully.";

    }, 1500); // Simulate API call delay
}