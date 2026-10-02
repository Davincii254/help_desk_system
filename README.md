# Help Desk Support System - Flask Learning Project

A small full-stack Flask project designed to make these concepts practical:

- RESTful API conventions
- CRUD operations
- Flask routes
- Registration and login
- Sessions
- Cookies
- Client-server communication
- Python data structures
- Algorithms and Big O notation

## 1. What the app does

A user must **register and log in** before accessing the help desk dashboard.

Once logged in, the user can:

- create a support ticket
- view all support tickets
- view ticket data returned by Flask
- update a ticket's status
- delete a ticket
- choose a preferred ticket filter
- inspect information sent from the browser to Flask

The project intentionally uses **Python lists and dictionaries instead of a database** so students can focus on Flask and computer-science concepts first.

---

## 2. Project structure

```text
help_desk_system/
|
|-- app.py
|-- requirements.txt
|-- README.md
|
|-- templates/
|   `-- index.html
|
`-- static/
    |-- styles.css
    `-- app.js
```

---

## 3. Setup

Create and activate a virtual environment, then install the requirements.

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install packages:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## 4. Main REST API routes

| Purpose | Method | Route | Typical success code |
|---|---|---|---:|
| Register | POST | `/api/register` | 201 |
| Login | POST | `/api/login` | 200 |
| Current user | GET | `/api/me` | 200 |
| Logout | POST | `/api/logout` | 200 |
| Read all tickets | GET | `/api/tickets` | 200 |
| Read one ticket | GET | `/api/tickets/<id>` | 200 |
| Create ticket | POST | `/api/tickets` | 201 |
| Update ticket | PATCH | `/api/tickets/<id>` | 200 |
| Delete ticket | DELETE | `/api/tickets/<id>` | 200 |
| Read cookie preference | GET | `/api/preferences` | 200 |
| Save cookie preference | POST | `/api/preferences` | 200 |
| Inspect client request | GET/POST | `/api/request-info` | 200 |

---

## 5. CRUD mapping

```text
CREATE -> POST
READ   -> GET
UPDATE -> PATCH
DELETE -> DELETE
```

Example ticket JSON:

```json
{
  "id": 3,
  "title": "Canvas page not loading",
  "category": "Platform",
  "priority": "High",
  "status": "Open",
  "description": "The dashboard stays blank after login.",
  "created_by": "mary"
}
```

---

## 6. Sessions

After a user logs in, the application stores:

```python
session["username"] = username
```

That lets Flask remember the user across later requests.

For example:

```text
POST /api/login
        |
        v
Flask saves username in session
        |
        v
GET /api/tickets
        |
        v
Flask checks session and knows who is logged in
```

The code includes comments around session creation, reading, and logout.

### Teaching question

Why don't we ask the user to send their username again every time they create or delete a ticket?

Because the session already maintains that login state across requests.

---

## 7. Cookies

The application uses a cookie named:

```text
ticket_filter
```

It stores a non-sensitive browser preference such as:

```text
Open
Closed
All
```

When the browser makes a later request, it automatically sends the cookie back to Flask.

This gives students a practical comparison:

```text
SESSION
Used here to remember WHO is logged in.

COOKIE
Used here to remember WHAT this browser prefers.
```

> Note: Flask's default session is itself implemented using a signed cookie. The project separates the two ideas for teaching purposes: application login state vs. a manually created preference cookie.

---

## 8. Client-server communication

The browser calls Flask using JavaScript `fetch()`.

Example:

```javascript
fetch("/api/tickets")
```

Flow:

```text
Browser / JavaScript
        |
        | HTTP request
        v
Flask route
        |
        | JSON response
        v
JavaScript
        |
        v
HTML updated on screen
```

The **Request Inspector** button calls `/api/request-info` and shows some of the data Flask receives from the client, including method, path, cookies, query parameters, logged-in user, and browser information.

---

## 9. Data structures

The application stores all tickets in a Python **list**:

```python
tickets = []
```

Each ticket is a Python **dictionary**:

```python
{
    "id": 1,
    "title": "Cannot log in",
    "priority": "High"
}
```

So students can connect:

```text
List       -> collection of tickets
Dictionary -> one ticket
Key/value  -> properties of the ticket
```

---

## 10. Algorithms and Big O

To find one ticket by ID, the application uses this style of search:

```python
for ticket in tickets:
    if ticket["id"] == ticket_id:
        return ticket
```

This is a **linear search**.

If there are `n` tickets, in the worst case Flask may inspect every ticket.

Therefore the time complexity is:

```text
O(n)
```

Compare that with directly accessing the first list item:

```python
tickets[0]
```

That is approximately:

```text
O(1)
```

A useful classroom discussion is: *How would the design change if the system had one million tickets?*

---

## 11. Suggested classroom walkthrough

1. Run the Flask application.
2. Register a new user.
3. Log in.
4. Open browser Developer Tools -> Network.
5. Create a ticket and inspect the POST request.
6. Refresh and inspect the GET request.
7. Update the ticket and locate the PATCH request.
8. Delete a ticket and locate the DELETE request.
9. Change the ticket filter and inspect browser cookies.
10. Click Request Inspector and connect browser data to Flask's `request` object.
11. Find `find_ticket()` in `app.py` and discuss why the search is O(n).

---

## 12. Good extension exercises

After students understand the basic version, ask them to try one or two of these:

- add a `Resolved` button
- allow filtering by priority
- add a search box for ticket title
- allow users to view only tickets they created
- count how many tickets are Open/Closed
- replace the list with a database later

Keep the first walkthrough simple. The main goal is understanding how the concepts connect.
