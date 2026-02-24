from flask import Blueprint, jsonify, render_template

base_bp = Blueprint('base', __name__)

@base_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "LifeIO Backend is running",
        "version": "1.0.0"
    }), 200

@base_bp.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@base_bp.route('/dashboard', methods=['GET'])
def dashboard():
    # Authentication check will be handled in frontend via JS or session
    return render_template('dashboard.html')

