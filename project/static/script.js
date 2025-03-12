document.getElementById("searchButton").addEventListener("click", async () => {
    const query = document.getElementById("query").value;

    if (query.trim() === "") {
        alert("Please enter a query.");
        return;
    }

    try {
        // Call the Flask API
        const response = await fetch("/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Parse JSON response
        const apiResponse = await response.json();
        console.log("API Response:", apiResponse); // Log the full API response for debugging

        // Use the API response directly as it is an array of results
        const results = Array.isArray(apiResponse) ? apiResponse : [];
        const resultsContainer = document.getElementById("results");
        resultsContainer.innerHTML = "";

        if (results.length === 0) {
            resultsContainer.innerHTML = "<p>No results found.</p>";
        } else {
            results.forEach(result => {
                const title = result.title || "No title available";
                const link = result.link || "#";
                const div = document.createElement("div");
                div.className = "result-item";
                div.innerHTML = `<a href="${link}" target="_blank">${title}</a>`;
                resultsContainer.appendChild(div);
            });
        }
    } catch (error) {
        console.error("Error fetching search results:", error);
        alert("An error occurred while fetching search results. Please try again.");
    }
});
