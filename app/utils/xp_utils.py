import math

def calculate_level(total_xp):
    """
    level = floor(total_xp / 500)
    """
    if total_xp < 0:
        return 0
    return math.floor(total_xp / 500)

def get_level_progress(total_xp):
    """
    Returns XP within the current level and required XP for next level.
    """
    current_level = calculate_level(total_xp)
    xp_in_current_level = total_xp % 500
    return {
        "level": current_level,
        "xp_current": round(xp_in_current_level, 2),
        "xp_needed": 500,
        "total_xp": round(total_xp, 2)
    }
