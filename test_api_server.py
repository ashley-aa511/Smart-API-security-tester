"""
Example Test API Server
A simple Flask API with intentional vulnerabilities for testing purposes
DO NOT USE IN PRODUCTION - FOR TESTING ONLY
"""

from flask import Flask, request, jsonify
import secrets

app = Flask(__name__)

# Fake database
users = {
    "1": {"id": "1", "name": "Alice", "email": "alice@example.com", "role": "user", "balance": 100},
    "2": {"id": "2", "name": "Bob", "email": "bob@example.com", "role": "user", "balance": 200},
    "admin": {"id": "admin", "name": "Admin", "email": "admin@example.com", "role": "admin", "balance": 999999}
}

# Rate limiting counter (simple demo)
request_counts = {}


@app.route('/')
def home():
    return jsonify({
        "message": "Test API Server",
        "version": "1.0.0",
        "endpoints": [
            "/api/user/<id>",
            "/api/users",
            "/api/admin",
            "/api/login"
        ]
    })


# VULNERABILITY: Broken Object Level Authorization
@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """BOLA vulnerability - no authorization check"""
    if user_id in users:
        return jsonify(users[user_id])
    return jsonify({"error": "User not found"}), 404


# VULNERABILITY: Missing authentication
@app.route('/api/admin', methods=['GET'])
def admin_panel():
    """Missing authentication on admin endpoint"""
    return jsonify({
        "message": "Admin panel",
        "users": users,
        "sensitive_data": "This should be protected!"
    })


# VULNERABILITY: Weak authentication
@app.route('/api/login', methods=['POST'])
def login():
    """Accepts weak passwords"""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    # Accepts weak passwords
    if username == "admin" and password in ["password", "123456", "admin"]:
        return jsonify({
            "token": secrets.token_hex(16),
            "message": "Login successful"
        })
    
    return jsonify({"error": "Invalid credentials"}), 401


# VULNERABILITY: Mass assignment
@app.route('/api/users', methods=['POST'])
def create_user():
    """Mass assignment vulnerability - accepts any fields"""
    data = request.get_json() or {}
    
    # Accepts isAdmin, role, balance without validation
    new_user = {
        "id": str(len(users) + 1),
        "name": data.get('name', 'Unknown'),
        "email": data.get('email', 'unknown@example.com'),
        "role": data.get('role', 'user'),  # Should be restricted!
        "isAdmin": data.get('isAdmin', False),  # Should be restricted!
        "balance": data.get('balance', 0)  # Should be restricted!
    }
    
    users[new_user['id']] = new_user
    return jsonify(new_user), 201


# VULNERABILITY: No rate limiting
@app.route('/api/unlimited', methods=['GET'])
def unlimited_endpoint():
    """No rate limiting - vulnerable to abuse"""
    return jsonify({"message": "Request processed", "count": len(request_counts)})


# VULNERABILITY: SQL Injection (simulated)
@app.route('/api/search', methods=['GET'])
def search():
    """Simulated SQL injection vulnerability"""
    query = request.args.get('q', '')
    
    # Simulated SQL error
    if "'" in query or "--" in query or "OR" in query.upper():
        return jsonify({
            "error": "SQL syntax error near '" + query + "'",
            "message": "sqlite3.OperationalError: unrecognized token"
        }), 500
    
    return jsonify({"results": [], "query": query})


# VULNERABILITY: Missing security headers
@app.after_request
def add_headers(response):
    """Intentionally missing security headers"""
    # NOT setting security headers for demo purposes
    return response


# API Documentation endpoint
@app.route('/api-docs', methods=['GET'])
def api_docs():
    """Publicly accessible API documentation"""
    return jsonify({
        "swagger": "2.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0"
        },
        "paths": {
            "/api/user/{id}": {
                "get": {"summary": "Get user by ID"}
            },
            "/api/admin": {
                "get": {"summary": "Admin panel (should be protected!)"}
            }
        }
    })


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════╗
║  TEST API SERVER - FOR TESTING PURPOSES ONLY             ║
║  Contains intentional vulnerabilities                    ║
║  DO NOT USE IN PRODUCTION                                ║
╚══════════════════════════════════════════════════════════╝

Starting server at http://localhost:5000

Test endpoints:
- http://localhost:5000/api/user/1 (BOLA)
- http://localhost:5000/api/admin (No auth)
- http://localhost:5000/api/login (Weak password)
- http://localhost:5000/api/users (Mass assignment)
- http://localhost:5000/api/search?q=test (SQL injection)
- http://localhost:5000/api-docs (Public docs)

Use this server with the security tester:
python3 main.py
Target: http://localhost:5000
    """)
    app.run(debug=True, port=5000)