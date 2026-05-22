let latestScanResult = null;

async function analyzeRepo() {
    const repo = document.getElementById("repoInput").value;
    const resultBox = document.getElementById("result");
    const downloadBtn = document.getElementById("downloadBtn");
    const dashboard = document.getElementById("dashboard");

    resultBox.innerHTML = `
        <div style="text-align:center; padding: 20px;">
            <p>Analyzing repository (this may take a minute)...</p>
            <div class="loader"></div>
        </div>
    `;
    downloadBtn.style.display = "none";
    dashboard.classList.add("hidden");
    latestScanResult = null;

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ repo })
        });

        const data = await response.json();
        if (data.detail[0].type == "value_error") {
            resultBox.innerHTML =
                "<pre>" + "✗  Invalid URL format. Expected: https://github.com/<owner>/<repo>" + "</pre>";
            return;
        }

        if (data.detail) {
            resultBox.innerHTML =
                "<pre>" + data.detail + "</pre>";
            return;
        }

        if (data.error) {
            resultBox.innerHTML =
                "<pre>" + data.error + "</pre>";
            return;
        }

        latestScanResult = data;
        renderDashboard(data);

        resultBox.innerHTML = "";
        downloadBtn.style.display = "inline-block";

    } catch (error) {
        resultBox.innerHTML = "Error contacting server.";
    }
}

function renderDashboard(data) {
    const scanInfo = data.scan_info;

    const score = scanInfo.repo_risk_score_100 || 0;

    document.getElementById("scoreValue").textContent = score;
    const statusEl = document.getElementById("repoStatus");
    statusEl.textContent = scanInfo.repo_status;

    if (scanInfo.repo_status.startsWith("SAFE")) {
        statusEl.style.color = "#19c37d"; // Green
    } else if (scanInfo.repo_status.startsWith("WARNING")) {
        statusEl.style.color = "#f5c542"; // Yellow
    } else {
        statusEl.style.color = "#ff4d4d"; // Red
    }

    document.getElementById("totalDeps").textContent = scanInfo.total_dependencies;
    document.getElementById("vulnFound").textContent = scanInfo.vulnerable_found;
    document.getElementById("zombiesFound").textContent = scanInfo.zombies_found;
    
    const needle = document.getElementById("needle");

    const angle = (score / 100) * 160 - 80;
    needle.style.transform = `rotate(${angle}deg)`;

    document.getElementById("dashboard").classList.remove("hidden");
}

function downloadJson() {
    if (!latestScanResult) {
        alert("No scan result available to download.");
        return;
    }

    const jsonData = JSON.stringify(latestScanResult, null, 2);
    const blob = new Blob([jsonData], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "dependency_scan_report.json";
    document.body.appendChild(link);
    link.click();

    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

window.analyzeRepo = analyzeRepo;
window.downloadJson = downloadJson;