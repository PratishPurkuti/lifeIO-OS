from flask import Blueprint, request, jsonify
from app.utils.supabase_client import get_supabase_client
from app.utils.middleware import login_required
from datetime import datetime

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/api/finance', methods=['POST'])
@login_required
def update_finance():
    data = request.get_json()
    date_str = data.get('date') # Format: YYYY-MM-DD
    income = data.get('income', 0)
    expense = data.get('expense', 0)

    if not date_str:
        return jsonify({"error": "Date is required"}), 400

    try:
        # Validate date format
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    supabase = get_supabase_client()

    new_record = {
        "user_id": request.user.id,
        "date": date_str,
        "income": float(income),
        "expense": float(expense)
    }

    try:
        # Upsert logic based on user_id and date
        res = supabase.table("daily_finance").upsert(
            new_record, 
            on_conflict="user_id,date"
        ).execute()
        return jsonify(res.data[0]), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@finance_bp.route('/api/finance', methods=['GET'])
@login_required
def get_finance_logs():
    supabase = get_supabase_client()
    res = supabase.table("daily_finance") \
        .select("*") \
        .eq("user_id", request.user.id) \
        .order("date", desc=True) \
        .execute()
    return jsonify(res.data), 200

@finance_bp.route('/api/finance/<log_id>', methods=['DELETE'])
@login_required
def delete_finance_log(log_id):
    supabase = get_supabase_client()
    res = supabase.table("daily_finance") \
        .delete() \
        .eq("id", log_id) \
        .eq("user_id", request.user.id) \
        .execute()
    return jsonify({"message": "Finance record deleted"}), 200
