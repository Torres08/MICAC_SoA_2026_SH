async function analyzeRepo() {

    const repo = document.getElementById("repoInput").value;

    const response = await fetch("/analyze", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({repo})
    });

    const data = await response.json();

    document.getElementById("result").textContent =
        JSON.stringify(data, null, 2);
}