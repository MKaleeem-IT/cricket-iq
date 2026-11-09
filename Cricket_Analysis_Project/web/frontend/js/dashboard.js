const API_BASE = "http://localhost:8000";

// Auth check
const token = localStorage.getItem("token");
const name = localStorage.getItem("name");

if (!token) {
    window.location.href = "/";
}

// Welcome message
if (name) {
    document.getElementById("welcome-text").textContent = `Welcome, ${name}`;
    document.getElementById("welcome-header").textContent = `Welcome back, ${name}! 🏏`;
    document.getElementById("user-avatar").textContent = name.charAt(0).toUpperCase();
}

// Logout
function logout() {
    localStorage.clear();
    window.location.href = "/";
}

// Load metrics
async function loadMetrics() {
    try {
        // Upcoming matches count
        const res = await fetch(`${API_BASE}/api/upcoming`);
        if (res.ok) {
            const data = await res.json();
            document.getElementById("metric-upcoming").textContent = data.metrics.total;
        }

        // Teams + matches count
        const optRes = await fetch(`${API_BASE}/api/options`);
        if (optRes.ok) {
            const optData = await optRes.json();
            document.getElementById("metric-teams").textContent = optData.teams.length;
        }

        // Matches count (static from known dataset)
        document.getElementById("metric-matches").textContent = "1,218";

    } catch (err) {
        console.error("Failed to load metrics:", err);
    }
}

loadMetrics();