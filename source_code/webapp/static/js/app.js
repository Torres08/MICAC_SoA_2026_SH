let latestScanResult = null;

async function analyzeRepo() {
    const repo = document.getElementById("repoInput").value;
    const resultBox = document.getElementById("result");
    const downloadBtn = document.getElementById("downloadBtn");
    const dashboard = document.getElementById("dashboard");

    resultBox.innerHTML = "Analyzing repository...";
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

        if (data.error || data.detail) {
            resultBox.innerHTML =
                "<pre>" + JSON.stringify(data, null, 2) + "</pre>";
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
    document.getElementById("repoStatus").textContent = scanInfo.repo_status;
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