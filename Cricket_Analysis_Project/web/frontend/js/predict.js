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

async function loadOptions() {
    try {
        const res = await fetch(`${API_BASE}/api/options`);
        const data = await res.json();

        const team1 = document.getElementById("team1");
        const team2 = document.getElementById("team2");
        const city = document.getElementById("city");
        const venue = document.getElementById("venue");

        team1.innerHTML = "";
        team2.innerHTML = "";

        data.teams.forEach(t => {
            team1.innerHTML += `<option value="${t}">${t}</option>`;
            team2.innerHTML += `<option value="${t}">${t}</option>`;
        });

        updateTeam2Options();

        city.innerHTML = "";
        data.cities.forEach(c => {
            city.innerHTML += `<option value="${c}">${c}</option>`;
        });

        venue.innerHTML = "";
        data.venues.forEach(v => {
            venue.innerHTML += `<option value="${v}">${v}</option>`;
        });

        updateTossWinner();

    } catch (err) {
        console.error("Failed to load options:", err);
        alert("Backend not reachable. Please start the server.");
    }
}

function updateTeam2Options() {
    const team1 = document.getElementById("team1").value;
    const team2 = document.getElementById("team2");

    Array.from(team2.options).forEach(opt => {
        opt.disabled = (opt.value === team1);
    });

    if (team2.value === team1) {
        const next = Array.from(team2.options).find(o => !o.disabled);
        team2.value = next ? next.value : "";
    }

    updateTossWinner();
}

function updateTossWinner() {
    const team1 = document.getElementById("team1").value;
    const team2 = document.getElementById("team2").value;
    const toss = document.getElementById("toss_winner");

    toss.innerHTML = "";
    if (team1) toss.innerHTML += `<option value="${team1}">${team1}</option>`;
    if (team2) toss.innerHTML += `<option value="${team2}">${team2}</option>`;
}

document.getElementById("team1").addEventListener("change", updateTeam2Options);

async function predictMatch() {
    const btn = document.getElementById("predict-btn");
    const result = document.getElementById("result");

    const payload = {
        team1: document.getElementById("team1").value,
        team2: document.getElementById("team2").value,
        city: document.getElementById("city").value,
        venue: document.getElementById("venue").value,
        toss_winner: document.getElementById("toss_winner").value,
        toss_decision: document.getElementById("toss_decision").value,
        year: parseInt(document.getElementById("year").value)
    };

    if (payload.team1 === payload.team2) {
        alert("Team 1 and Team 2 must be different");
        return;
    }

    btn.textContent = "⏳ Predicting...";
    btn.disabled = true;
    result.innerHTML = "";

    try {
        const res = await fetch(`${API_BASE}/api/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
            result.innerHTML = `<div class="message error">${data.detail || "Prediction failed"}</div>`;
            return;
        }

        result.innerHTML = `
            <div class="prediction-card">
                <div style="color:#94A3B8; font-size:13px; font-weight:700;">
                    MACHINE LEARNING PREDICTION
                </div>
                <div style="font-size:45px; margin:12px 0;">🏆</div>
                <div class="winner-text">${data.winner}</div>
                <div style="color:#CBD5E1; margin-top:8px;">
                    Predicted Match Winner
                </div>
            </div>

            <div class="section-title">📊 Prediction Probabilities</div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="metric-card">
                    <div class="metric-label">${data.team1}</div>
                    <div class="metric-value accent">${data.team1_probability}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">${data.team2}</div>
                    <div class="metric-value">${data.team2_probability}%</div>
                </div>
            </div>
        `;

    } catch (err) {
        result.innerHTML = `<div class="message error">Network error: ${err.message}</div>`;
    } finally {
        btn.textContent = "⚡ PREDICT MATCH WINNER";
        btn.disabled = false;
    }
}

loadOptions();