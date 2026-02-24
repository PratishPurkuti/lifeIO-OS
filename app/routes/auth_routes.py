from flask import Blueprint, request, jsonify, make_response
from app.utils.supabase_client import get_supabase_client
from app.utils.middleware import login_required, admin_only
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    # Enforce ADMIN_EMAIL restriction
    admin_email = os.getenv('ADMIN_EMAIL')
    if email != admin_email:
        return jsonify({"error": "Unauthorized email address"}), 403

    supabase = get_supabase_client()
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            res = make_response(jsonify({
                "message": "Login successful",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                }
            }), 200)
            
            # Set session cookie
            res.set_cookie(
                'sb-access-token', 
                response.session.access_token,
                httponly=True,
                secure=True, # Should be True in production
                samesite='Lax'
            )
            return res
        else:
            return jsonify({"error": "Authentication failed"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    res = make_response(jsonify({"message": "Logged out"}), 200)
    res.delete_cookie('sb-access-token')
    return res

@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def me():
    return jsonify({
        "id": request.user.id,
        "email": request.user.email
    }), 200
