from flask import Blueprint, request, jsonify
from app.utils.supabase_client import get_supabase_client
from app.utils.middleware import login_required
from datetime import datetime
import dateutil.parser

sleep_bp = Blueprint('sleep', __name__)

@sleep_bp.route('/api/sleep', methods=['POST'])
@login_required
def add_sleep_log():
    data = request.get_json()
    sleep_time_str = data.get('sleep_time')
    wake_time_str = data.get('wake_time')
    quality = data.get('quality')

    if not sleep_time_str or not wake_time_str or quality is None:
        return jsonify({"error": "sleep_time, wake_time, and quality are required"}), 400

    try:
        sleep_time = dateutil.parser.isoparse(sleep_time_str)
        wake_time = dateutil.parser.isoparse(wake_time_str)
        quality = int(quality)
    except Exception as e:
        return jsonify({"error": "Invalid data format"}), 400

    # Validation
    if wake_time <= sleep_time:
        return jsonify({"error": "Wake time must be after sleep time"}), 400
    
    if quality < 1 or quality > 5:
        return jsonify({"error": "Quality must be between 1 and 5"}), 400

    supabase = get_supabase_client()

    new_log = {
        "user_id": request.user.id,
        "sleep_time": sleep_time.isoformat(),
        "wake_time": wake_time.isoformat(),
        "quality": quality
    }

    try:
        res = supabase.table("sleep_logs").insert(new_log).execute()
        return jsonify(res.data[0]), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@sleep_bp.route('/api/sleep', methods=['GET'])
@login_required
def get_sleep_logs():
    supabase = get_supabase_client()
    res = supabase.table("sleep_logs") \
        .select("*") \
        .eq("user_id", request.user.id) \
        .order("sleep_time", desc=True) \
        .execute()
    return jsonify(res.data), 200

@sleep_bp.route('/api/sleep/<log_id>', methods=['DELETE'])
@login_required
def delete_sleep_log(log_id):
    supabase = get_supabase_client()
    res = supabase.table("sleep_logs") \
        .delete() \
        .eq("id", log_id) \
        .eq("user_id", request.user.id) \
        .execute()
    return jsonify({"message": "Sleep log deleted"}), 200
