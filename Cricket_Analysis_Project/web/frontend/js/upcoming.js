const API_BASE = "http://localhost:8000";

const token = localStorage.getItem("token");
const name = localStorage.getItem("name");

if (!token) {
    window.location.href = "/";
}

if (name) {
    document.getElementById("welcome-text").textContent = `Welcome, ${name}`;
    document.getElementById("user-avatar").textContent = name.charAt(0).toUpperCase();
}

function logout() {
    localStorage.clear();
    window.location.href = "/";
}

async function loadUpcoming() {
    try {
        const res = await fetch(`${API_BASE}/api/upcoming`);
        const data = await res.json();

        // Metrics
        document.getElementById("m-total").textContent = data.metrics.total;
        document.getElementById("m-preds").textContent = data.metrics.predictions;
        document.getElementById("m-wait").textContent = data.metrics.waiting;

        // Fixtures list
        const fixturesList = document.getElementById("fixtures-list");
        if (data.fixtures.length === 0) {
            fixturesList.innerHTML = `<p style="color:#94A3B8;">No upcoming fixtures available.</p>`;
        } else {
            fixturesList.innerHTML = data.fixtures.map(f => `
                <div class="info-card" style="margin-bottom: 16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <strong>🏏 ${f.team1} vs ${f.team2}</strong>
                        ${f.has_prediction
                            ? '<span style="color:#4ADE80; font-weight:700; font-size:13px;">🔮 Prediction available</span>'
                            : '<span style="color:#94A3B8; font-weight:600; font-size:13px;">⏳ No prediction</span>'
                        }
                    </div>
                    <div style="color:#94A3B8; font-size:13px;">
                        ${f.competition} | ${formatTime(f.time)}
                    </div>
                </div>
            `).join("");
        }

        // Predictions list
        const predsList = document.getElementById("predictions-list");
        if (data.predictions.length === 0) {
            predsList.innerHTML = `<p style="color:#94A3B8;">No upcoming match has enough team history for a prediction.</p>`;
        } else {
            predsList.innerHTML = data.predictions.map(p => `
                <div class="info-card" style="margin-bottom: 16px;">
                    <div style="margin-bottom: 8px;">
                        <strong>🏏 ${p.team1} vs ${p.team2}</strong>
                    </div>
                    <div style="color:#94A3B8; font-size:13px; margin-bottom: 12px;">
                        ${p.category} | ${p.competition} | ${formatTime(p.match_time)}
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 12px;">
                        <div>
                            <strong>${p.team1}</strong><br>
                            <span style="color:#94A3B8; font-size:13px;">Recent: ${p.team1_recent_form}</span><br>
                            <span style="color:#94A3B8; font-size:13px;">Total history: ${p.team1_total_history}</span>
                        </div>
                        <div>
                            <strong>${p.team2}</strong><br>
                            <span style="color:#94A3B8; font-size:13px;">Recent: ${p.team2_recent_form}</span><br>
                            <span style="color:#94A3B8; font-size:13px;">Total history: ${p.team2_total_history}</span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 12px;">
                        <div class="metric-card" style="padding:16px;">
                            <div class="metric-label">${p.team1} share</div>
                            <div class="metric-value accent">${p.team1_estimated_share}%</div>
                        </div>
                        <div class="metric-card" style="padding:16px;">
                            <div class="metric-label">${p.team2} share</div>
                            <div class="metric-value">${p.team2_estimated_share}%</div>
                        </div>
                    </div>
                    <div style="background: linear-gradient(135deg, #17243A, #1D3049); border:1px solid #3A5273; border-radius: 12px; padding: 16px; text-align:center;">
                        <div style="color:#94A3B8; font-size:12px; font-weight:700; text-transform:uppercase;">Predicted Winner</div>
                        <div style="color:#4ADE80; font-size:22px; font-weight:800; margin-top:6px;">${p.predicted_winner}</div>
                        <div style="color:#94A3B8; font-size:12px; margin-top:4px;">${p.data_confidence}</div>
                    </div>
                </div>
            `).join("");
        }

    } catch (err) {
        console.error("Failed to load upcoming:", err);
        document.getElementById("fixtures-list").innerHTML = `<div class="message error">Network error: ${err.message}</div>`;
        document.getElementById("predictions-list").innerHTML = "";
    }
}

function formatTime(t) {
    if (!t) return "";
    try {
        const d = new Date(t);
        return d.toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' });
    } catch {
        return t;
    }
}

loadUpcoming();