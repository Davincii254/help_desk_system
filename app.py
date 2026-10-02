from flask import Flask, render_template, request, jsonify, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Flask uses SECRET_KEY to sign the session cookie.
# This helps Flask detect if someone has tampered with the session data.
# In a real application, this value should come from an environment variable.
app.secret_key = "help-desk-demo-secret"


# -----------------------------------------------------------------------------
# IN-MEMORY DATA
# -----------------------------------------------------------------------------
# We are using Python lists so that students can focus on Flask concepts first.
# Restarting the app will reset the data. A database can be introduced later.
users = []
tickets = [
    {
        "id": 1,
        "title": "Cannot access student portal",
        "category": "Account",
        "priority": "High",
        "status": "Open",
        "description": "Login keeps returning an invalid credentials message.",
        "created_by": "demo",
    },
    {
        "id": 2,
        "title": "Wi-Fi is slow",
        "category": "Network",
        "priority": "Medium",
        "status": "Open",
        "description": "Connection becomes very slow during afternoon classes.",
        "created_by": "demo",
    },
]


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def current_username():
    """Return the logged-in username stored in the Flask session."""
    return session.get("username")


def login_required_json():
    """Simple helper used by API routes that require a logged-in user."""
    if not current_username():
        return jsonify({"error": "Login required"}), 401
    return None


def find_ticket(ticket_id):
    """
    Search for a ticket by ID.

    This is a LINEAR SEARCH because we may need to check each ticket one by one.
    If there are n tickets, the worst-case time complexity is O(n).
    """
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    return None


# -----------------------------------------------------------------------------
# PAGE ROUTES
# -----------------------------------------------------------------------------
@app.route("/")
def home():
    """Serve the single-page user interface."""
    return render_template("index.html")


# -----------------------------------------------------------------------------
# AUTHENTICATION ROUTES
# -----------------------------------------------------------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Check whether the username already exists.
    if any(user["username"] == username for user in users):
        return jsonify({"error": "Username already exists"}), 409

    # We hash passwords instead of storing them as plain text.
    users.append(
        {
            "id": len(users) + 1,
            "username": username,
            "password_hash": generate_password_hash(password),
        }
    )

    return jsonify({"message": "Registration successful. You can now log in."}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = next((u for u in users if u["username"] == username), None)

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    # -------------------------------------------------------------------------
    # SESSION EXAMPLE
    # -------------------------------------------------------------------------
    # A session helps Flask remember information across multiple requests.
    # After login, we save the username in the session.
    # On later requests, Flask can read session["username"] and know who is using
    # the application without asking for the username again on every request.
    # Flask's default session is stored in a signed cookie in the browser.
    session["username"] = username

    return jsonify({"message": "Login successful", "username": username}), 200


@app.route("/api/logout", methods=["POST"])
def logout():
    # Removing the username from the session logs the user out.
    session.pop("username", None)
    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/api/me", methods=["GET"])
def me():
    username = current_username()
    if not username:
        return jsonify({"logged_in": False}), 200

    return jsonify({"logged_in": True, "username": username}), 200


# -----------------------------------------------------------------------------
# CRUD ROUTES - HELP DESK TICKETS
# -----------------------------------------------------------------------------
@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    auth_error = login_required_json()
    if auth_error:
        return auth_error

    # READ all tickets
    return jsonify(tickets), 200


@app.route("/api/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    auth_error = login_required_json()
    if auth_error:
        return auth_error

    # READ one ticket using the O(n) linear search helper above.
    ticket = find_ticket(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    return jsonify(ticket), 200


@app.route("/api/tickets", methods=["POST"])
def create_ticket():
    auth_error = login_required_json()
    if auth_error:
        return auth_error

    data = request.get_json() or {}

    title = data.get("title", "").strip()
    category = data.get("category", "").strip()
    priority = data.get("priority", "").strip()
    description = data.get("description", "").strip()

    if not title or not category or not priority:
        return jsonify({"error": "Title, category and priority are required"}), 400

    new_ticket = {
        "id": max([ticket["id"] for ticket in tickets], default=0) + 1,
        "title": title,
        "category": category,
        "priority": priority,
        "status": "Open",
        "description": description,
        "created_by": current_username(),
    }

    tickets.append(new_ticket)
    return jsonify(new_ticket), 201


@app.route("/api/tickets/<int:ticket_id>", methods=["PATCH"])
def update_ticket(ticket_id):
    auth_error = login_required_json()
    if auth_error:
        return auth_error

    ticket = find_ticket(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    data = request.get_json() or {}

    # PATCH means we update only the fields provided by the client.
    allowed_fields = ["title", "category", "priority", "status", "description"]
    for field in allowed_fields:
        if field in data:
            ticket[field] = data[field]

    return jsonify(ticket), 200


@app.route("/api/tickets/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    auth_error = login_required_json()
    if auth_error:
        return auth_error

    ticket = find_ticket(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    tickets.remove(ticket)
    return jsonify({"message": "Ticket deleted successfully"}), 200


# -----------------------------------------------------------------------------
# COOKIE ROUTES
# -----------------------------------------------------------------------------
@app.route("/api/preferences", methods=["GET"])
def get_preferences():
    """
    Read a simple browser preference from a cookie.

    COOKIE EXAMPLE:
    A cookie is small data stored by the browser and sent back to the server on
    later requests. Here we use it for a non-sensitive preference: which ticket
    status the user wants to see first.
    """
    preferred_filter = request.cookies.get("ticket_filter", "All")
    return jsonify({"ticket_filter": preferred_filter}), 200


@app.route("/api/preferences", methods=["POST"])
def save_preferences():
    auth_error = login_required_json()
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    ticket_filter = data.get("ticket_filter", "All")

    response = make_response(
        jsonify({"message": "Preference saved", "ticket_filter": ticket_filter})
    )

    # -------------------------------------------------------------------------
    # COOKIE EXAMPLE
    # -------------------------------------------------------------------------
    # set_cookie() tells the browser to remember a value.
    # The browser sends this cookie back automatically on later requests.
    # We use max_age so it can remain after the browser is refreshed/reopened.
    # We are NOT storing a password or other sensitive information here.
    response.set_cookie("ticket_filter", ticket_filter, max_age=60 * 60 * 24 * 7)

    return response, 200


# -----------------------------------------------------------------------------
# CLIENT-SERVER / REQUEST INSPECTOR
# -----------------------------------------------------------------------------
@app.route("/api/request-info", methods=["GET", "POST"])
def request_info():
    """Return information Flask received from the client/browser."""
    return jsonify(
        {
            "method": request.method,
            "path": request.path,
            "query_parameters": request.args.to_dict(),
            "json_body": request.get_json(silent=True),
            "cookies": request.cookies.to_dict(),
            "logged_in_user": current_username(),
            "user_agent": request.headers.get("User-Agent"),
        }
    ), 200


if __name__ == "__main__":
    app.run(debug=True)
