const authSection = document.getElementById("authSection");
const appSection = document.getElementById("appSection");
const userBadge = document.getElementById("userBadge");
const ticketList = document.getElementById("ticketList");
const ticketFilter = document.getElementById("ticketFilter");

let allTickets = [];

async function api(url, options = {}) {
    const response = await fetch(url, {
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        ...options,
    });

    const data = await response.json().catch(() => ({}));
    return { response, data };
}

async function checkLogin() {
    const { data } = await api("/api/me");

    if (data.logged_in) {
        authSection.classList.add("hidden");
        appSection.classList.remove("hidden");
        userBadge.classList.remove("hidden");
        userBadge.textContent = `Logged in: ${data.username}`;
        await loadPreference();
        await loadTickets();
    } else {
        authSection.classList.remove("hidden");
        appSection.classList.add("hidden");
        userBadge.classList.add("hidden");
    }
}

document.getElementById("registerForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const { response, data } = await api("/api/register", {
        method: "POST",
        body: JSON.stringify({
            username: document.getElementById("registerUsername").value,
            password: document.getElementById("registerPassword").value,
        }),
    });

    const message = document.getElementById("registerMessage");
    message.textContent = data.message || data.error || "Something went wrong";
    message.style.color = response.ok ? "#18794e" : "#b42318";
});

document.getElementById("loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const { response, data } = await api("/api/login", {
        method: "POST",
        body: JSON.stringify({
            username: document.getElementById("loginUsername").value,
            password: document.getElementById("loginPassword").value,
        }),
    });

    const message = document.getElementById("loginMessage");
    message.textContent = data.message || data.error || "Something went wrong";
    message.style.color = response.ok ? "#18794e" : "#b42318";

    if (response.ok) {
        await checkLogin();
    }
});

document.getElementById("logoutButton").addEventListener("click", async () => {
    await api("/api/logout", { method: "POST" });
    await checkLogin();
});

document.getElementById("ticketForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const { response, data } = await api("/api/tickets", {
        method: "POST",
        body: JSON.stringify({
            title: document.getElementById("ticketTitle").value,
            category: document.getElementById("ticketCategory").value,
            priority: document.getElementById("ticketPriority").value,
            description: document.getElementById("ticketDescription").value,
        }),
    });

    if (!response.ok) {
        alert(data.error || "Could not create ticket");
        return;
    }

    event.target.reset();
    await loadTickets();
});

async function loadTickets() {
    const { response, data } = await api("/api/tickets");
    if (!response.ok) return;

    allTickets = data;
    renderTickets();
}

function renderTickets() {
    const filter = ticketFilter.value;
    const visibleTickets = filter === "All"
        ? allTickets
        : allTickets.filter(ticket => ticket.status === filter);

    if (visibleTickets.length === 0) {
        ticketList.innerHTML = "<p>No tickets match this filter.</p>";
        return;
    }

    ticketList.innerHTML = visibleTickets.map(ticket => `
        <div class="ticket-card">
            <h4>#${ticket.id} — ${escapeHtml(ticket.title)}</h4>
            <div class="ticket-meta">
                <span class="badge">${escapeHtml(ticket.category)}</span>
                <span class="badge">Priority: ${escapeHtml(ticket.priority)}</span>
                <span class="badge">Status: ${escapeHtml(ticket.status)}</span>
            </div>
            <p>${escapeHtml(ticket.description || "No description")}</p>
            <small>Created by: ${escapeHtml(ticket.created_by || "Unknown")}</small>
            <div class="ticket-actions">
                <button class="small secondary" onclick="updateTicket(${ticket.id})">Update Status</button>
                <button class="small danger" onclick="deleteTicket(${ticket.id})">Delete</button>
            </div>
        </div>
    `).join("");
}

async function updateTicket(id) {
    const status = prompt("Enter status: Open, In Progress, or Closed");
    if (!status) return;

    const allowed = ["Open", "In Progress", "Closed"];
    if (!allowed.includes(status)) {
        alert("Please enter Open, In Progress, or Closed");
        return;
    }

    const { response, data } = await api(`/api/tickets/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
    });

    if (!response.ok) {
        alert(data.error || "Could not update ticket");
        return;
    }

    await loadTickets();
}

async function deleteTicket(id) {
    if (!confirm("Delete this ticket?")) return;

    const { response, data } = await api(`/api/tickets/${id}`, {
        method: "DELETE",
    });

    if (!response.ok) {
        alert(data.error || "Could not delete ticket");
        return;
    }

    await loadTickets();
}

async function loadPreference() {
    const { data } = await api("/api/preferences");
    ticketFilter.value = data.ticket_filter || "All";
}

ticketFilter.addEventListener("change", async () => {
    // The front end asks Flask to save this preference as a browser cookie.
    await api("/api/preferences", {
        method: "POST",
        body: JSON.stringify({ ticket_filter: ticketFilter.value }),
    });

    renderTickets();
});

document.getElementById("inspectButton").addEventListener("click", async () => {
    const { data } = await api("/api/request-info?source=dashboard");
    document.getElementById("requestOutput").textContent = JSON.stringify(data, null, 2);
});

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

checkLogin();
