from functools import wraps
from flask import request, jsonify, session, current_app
from app.utils.supabase_client import get_supabase_client
import os

def get_token():
    # Check Authorization header first, then cookie
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return request.cookies.get('sb-access-token')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token()
        if not token:
            return jsonify({"error": "Unauthorized"}), 401
        
        supabase = get_supabase_client()
        try:
            # Set the session token so RLS works
            supabase.postgrest.auth(token)
            
            # Validate token with Supabase
            user_response = supabase.auth.get_user(token)
            if not user_response.user:
                return jsonify({"error": "Invalid token"}), 401
            
            # Attach user to request context for easy access
            request.user = user_response.user
        except Exception as e:
            return jsonify({"error": str(e)}), 401
            
        return f(*args, **kwargs)
    return decorated_function

def admin_only(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        admin_email = os.getenv('ADMIN_EMAIL')
        if not request.user or request.user.email != admin_email:
            return jsonify({"error": "Forbidden: Admin access only"}), 403
        return f(*args, **kwargs)
    return decorated_function

