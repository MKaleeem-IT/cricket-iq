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

// Load team list
async function loadTeams() {
    try {
        const res = await fetch(`${API_BASE}/api/options`);
        const data = await res.json();

        const sel = document.getElementById("team-select");
        sel.innerHTML = '<option value="">-- Select a team --</option>';
        data.teams.forEach(t => {
            sel.innerHTML += `<option value="${t}">${t}</option>`;
        });

    } catch (err) {
        console.error("Failed to load teams:", err);
        alert("Backend not reachable.");
    }
}

// Load stats for selected team
async function loadStats(team) {
    if (!team) {
        document.getElementById("stats-container").style.display = "none";
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/api/stats/${encodeURIComponent(team)}`);
        const data = await res.json();

        if (!res.ok) {
            alert(data.detail || "Failed to load stats");
            return;
        }

        document.getElementById("s-played").textContent = data.played;
        document.getElementById("s-won").textContent = data.won;
        document.getElementById("s-lost").textContent = data.lost;
        document.getElementById("s-pct").textContent = data.win_percentage + "%";

        // Match history
        const hist = document.getElementById("history-list");
        if (data.history.length === 0) {
            hist.innerHTML = `<p style="color:#94A3B8;">No matches found.</p>`;
        } else {
            hist.innerHTML = `
                <div class="info-card" style="padding: 0; overflow: hidden;">
                    <table style="width:100%; border-collapse: collapse; font-size: 14px;">
                        <thead>
                            <tr style="background:#111B2E; color:#94A3B8; text-align:left;">
                                <th style="padding: 12px 16px;">Date</th>
                                <th style="padding: 12px 16px;">Team 1</th>
                                <th style="padding: 12px 16px;">Team 2</th>
                                <th style="padding: 12px 16px;">Winner</th>
                                <th style="padding: 12px 16px;">City</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.history.map(m => `
                                <tr style="border-top:1px solid #293B57;">
                                    <td style="padding: 10px 16px; color:#CBD5E1;">${m.date}</td>
                                    <td style="padding: 10px 16px;">${m.team1}</td>
                                    <td style="padding: 10px 16px;">${m.team2}</td>
                                    <td style="padding: 10px 16px; color:#4ADE80; font-weight:600;">${m.winner}</td>
                                    <td style="padding: 10px 16px; color:#94A3B8;">${m.city}</td>
                                </tr>
                            `).join("")}
                        </tbody>
                    </table>
                </div>
            `;
        }

        document.getElementById("stats-container").style.display = "block";

    } catch (err) {
        console.error("Failed to load stats:", err);
        alert("Network error: " + err.message);
    }
}

document.getElementById("team-select").addEventListener("change", (e) => {
    loadStats(e.target.value);
});

loadTeams();