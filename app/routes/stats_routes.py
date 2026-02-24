from flask import Blueprint, jsonify, request
from app.utils.supabase_client import get_supabase_client
from app.utils.middleware import login_required
from app.utils.xp_utils import get_level_progress
from datetime import datetime, timedelta
import pytz

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/api/stats/summary', methods=['GET'])
@login_required
def get_summary():
    supabase = get_supabase_client()
    user_id = request.user.id
    
    # 1. Get Lifetime XP (Sum of all activities)
    act_res = supabase.table("activities") \
        .select("xp_earned") \
        .eq("user_id", user_id) \
        .execute()
    
    total_xp = sum(item['xp_earned'] for item in act_res.data) if act_res.data else 0
    level_info = get_level_progress(total_xp)

    # 2. Get Monthly XP
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    month_res = supabase.table("activities") \
        .select("xp_earned") \
        .eq("user_id", user_id) \
        .gte("start_time", start_of_month) \
        .execute()
    monthly_xp = sum(item['xp_earned'] for item in month_res.data) if month_res.data else 0

    # 3. Get Today XP
    start_of_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    today_res = supabase.table("activities") \
        .select("xp_earned") \
        .eq("user_id", user_id) \
        .gte("start_time", start_of_today) \
        .execute()
    today_xp = sum(item['xp_earned'] for item in today_res.data) if today_res.data else 0

    return jsonify({
        "level": level_info['level'],
        "xp_stats": {
            "total": level_info['total_xp'],
            "current_level_progress": level_info['xp_current'],
            "needed_for_next": level_info['xp_needed'],
            "monthly": round(monthly_xp, 2),
            "today": round(today_xp, 2)
        }
    }), 200

@stats_bp.route('/api/stats/skills', methods=['GET'])
@login_required
def get_skills():
    supabase = get_supabase_client()
    user_id = request.user.id
    
    # Get XP grouped by category
    res = supabase.table("activities") \
        .select("category, xp_earned") \
        .eq("user_id", user_id) \
        .execute()
    
    skills = {}
    if res.data:
        for item in res.data:
            cat = item['category']
            skills[cat] = skills.get(cat, 0) + item['xp_earned']
            
    # Round values
    formatted_skills = {k: round(v, 2) for k, v in skills.items()}
    
    return jsonify(formatted_skills), 200

@stats_bp.route('/api/stats/finance', methods=['GET'])
@login_required
def get_finance_summary():
    supabase = get_supabase_client()
    user_id = request.user.id
    
    # Get last 30 days of finance
    thirty_days_ago = (datetime.now() - timedelta(days=30)).date().isoformat()
    res = supabase.table("daily_finance") \
        .select("income, expense") \
        .eq("user_id", user_id) \
        .gte("date", thirty_days_ago) \
        .execute()
    
    total_income = sum(item['income'] for item in res.data) if res.data else 0
    total_expense = sum(item['expense'] for item in res.data) if res.data else 0
    
    return jsonify({
        "period": "Last 30 days",
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "net": float(total_income - total_expense)
    }), 200
