from datetime import datetime, time, timedelta
import pytz

def get_midnight_of_day(dt):
    """Returns the midnight (end of day) for a given datetime."""
    return datetime.combine(dt.date(), time.max).replace(tzinfo=dt.tzinfo)

def calculate_xp(duration_minutes, multiplier):
    """
    1 hour = 60 base XP.
    XP = (duration / 60) * 60 * multiplier = duration * multiplier.
    """
    return float(duration_minutes) * float(multiplier)

def truncate_to_midnight(start_time, end_time):
    """If end_time cross midnight, truncate it to midnight of the start day."""
    midnight = get_midnight_of_day(start_time)
    if end_time > midnight:
        return midnight
    return end_time

def check_overlap(supabase, user_id, start_time, end_time):
    """
    Checks for overlapping activities and returns them.
    Logic: (StartA < EndB) AND (EndA > StartB)
    """
    # If end_time is None, we assume it's "now" or "ongoing"
    # But for life tracking, we'll usually provide an end time or auto-stop.
    query = supabase.table("activities") \
        .select("*") \
        .eq("user_id", user_id) \
        .lt("start_time", end_time.isoformat()) \
        .gt("end_time", start_time.isoformat())
    
    result = query.execute()
    return result.data
