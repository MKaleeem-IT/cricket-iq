const API_BASE = "http://localhost:8000";

function showMessage(text, type = "error") {
    const el = document.getElementById("message");
    if (!el) return;
    el.textContent = text;
    el.className = `message ${type}`;
    el.classList.remove("hidden");
}

function hideMessage() {
    const el = document.getElementById("message");
    if (el) el.classList.add("hidden");
}

function showSignup(e) {
    if (e) e.preventDefault();
    hideMessage();
    document.getElementById("login-form").classList.add("hidden");
    document.getElementById("signup-form").classList.remove("hidden");
}

function showLogin(e) {
    if (e) e.preventDefault();
    hideMessage();
    document.getElementById("signup-form").classList.add("hidden");
    document.getElementById("login-form").classList.remove("hidden");
}

async function handleLogin() {
    hideMessage();
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;

    if (!email || !password) {
        showMessage("Please fill all fields", "error");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/api/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            showMessage(data.detail || "Login failed", "error");
            return;
        }

        localStorage.setItem("token", data.token);
        localStorage.setItem("name", data.name);
        localStorage.setItem("email", data.email);

        showMessage("Login successful! Redirecting...", "success");
        setTimeout(() => {
            window.location.href = "/dashboard.html";
        }, 500);

    } catch (err) {
        showMessage("Network error: " + err.message, "error");
    }
}

async function handleSignup() {
    hideMessage();
    const name = document.getElementById("signup-name").value.trim();
    const email = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-password").value;

    if (!name || !email || !password) {
        showMessage("Please fill all fields", "error");
        return;
    }

    if (password.length < 6) {
        showMessage("Password must be at least 6 characters", "error");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/api/auth/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            showMessage(data.detail || "Signup failed", "error");
            return;
        }

        showMessage("Account created! Please sign in.", "success");
        document.getElementById("login-email").value = email;
        setTimeout(showLogin, 800);

    } catch (err) {
        showMessage("Network error: " + err.message, "error");
    }
}