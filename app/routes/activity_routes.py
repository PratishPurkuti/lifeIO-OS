from flask import Blueprint, request, jsonify
from app.utils.supabase_client import get_supabase_client, get_supabase_admin
from app.utils.middleware import login_required
from app.utils.activity_utils import calculate_xp, truncate_to_midnight, get_midnight_of_day
from datetime import datetime
import dateutil.parser

activity_bp = Blueprint('activities', __name__)

@activity_bp.route('/api/activities', methods=['POST'])
@login_required
def add_activity():
    data = request.get_json()
    category_name = data.get('category')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')

    if not category_name or not start_time_str:
        return jsonify({"error": "Category and start_time are required"}), 400

    start_time = dateutil.parser.isoparse(start_time_str)
    
    # Auto-stop at midnight if end_time not provided
    if not end_time_str:
        end_time = get_midnight_of_day(start_time)
    else:
        end_time = dateutil.parser.isoparse(end_time_str)
        # Requirement: activities auto-stop at midnight
        end_time = truncate_to_midnight(start_time, end_time)

    supabase = get_supabase_client()

    # 1. Fetch category multiplier
    cat_res = supabase.table("categories") \
        .select("xp_multiplier") \
        .eq("user_id", request.user.id) \
        .eq("name", category_name) \
        .execute()
    
    if not cat_res.data:
        # Failsafe: Create default multipliers if category is missing
        multipliers = {
            "Work": 1.2,
            "Study": 1.1,
            "Workout": 1.3,
            "Cooking": 1.0,
            "Wasted Time": -1.0
        }
        multiplier = multipliers.get(category_name, 1.0)
        admin_client = get_supabase_admin()
        if admin_client:
            admin_client.table("categories").insert({
                "user_id": request.user.id,
                "name": category_name,
                "xp_multiplier": multiplier
            }).execute()
        else:
            # Fallback to regular client if admin not configured
            supabase.table("categories").insert({
                "user_id": request.user.id,
                "name": category_name,
                "xp_multiplier": multiplier
            }).execute()
    else:
        multiplier = cat_res.data[0]['xp_multiplier']

    # 2. Handle overlaps (Replace/Override)
    # Logic: Delete any activity that fully or partially overlaps with the new one
    # This simplifies the "new one overrides" rule.
    supabase.table("activities") \
        .delete() \
        .eq("user_id", request.user.id) \
        .lt("start_time", end_time.isoformat()) \
        .gt("end_time", start_time.isoformat()) \
        .execute()

    # 3. Calculate XP
    duration_minutes = (end_time - start_time).total_seconds() / 60
    xp_earned = calculate_xp(duration_minutes, multiplier)

    # 4. Insert new activity
    new_activity = {
        "user_id": request.user.id,
        "category": category_name,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "xp_earned": xp_earned
    }

    res = supabase.table("activities").insert(new_activity).execute()
    
    return jsonify(res.data[0]), 201

@activity_bp.route('/api/activities', methods=['GET'])
@login_required
def get_activities():
    supabase = get_supabase_client()
    res = supabase.table("activities") \
        .select("*") \
        .eq("user_id", request.user.id) \
        .order("start_time", desc=True) \
        .execute()
    return jsonify(res.data), 200

@activity_bp.route('/api/activities/<activity_id>', methods=['DELETE'])
@login_required
def delete_activity(activity_id):
    supabase = get_supabase_client()
    res = supabase.table("activities") \
        .delete() \
        .eq("id", activity_id) \
        .eq("user_id", request.user.id) \
        .execute()
    return jsonify({"message": "Activity deleted"}), 200
