import svgwrite
from themes.styles import THEMES
from .svg_base import create_svg_base


def draw_trophy_card(data, theme_name="Default", custom_colors=None):
    """
    Generates the GitHub Trophy Card SVG showing achievements.
    
    data: dict with user stats including:
        - username
        - total_stars
        - followers
        - public_repos
        - top_repos (list of repos with 'forks' key)
        - created_at (account creation date)
    theme_name: string key from THEMES
    custom_colors: optional dict to override theme colors
    """
    width = 450
    height = 320
    
    # Calculate total forks from all repositories
    total_forks = sum(repo.get("forks", 0) for repo in data.get("top_repos", []))
    
    # Calculate years of contribution (from account creation)
    created_at = data.get("created_at", "")
    years_contributing = 0
    if created_at:
        try:
            from datetime import datetime
            created_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
            years_contributing = (datetime.now() - created_date).days // 365
            if years_contributing < 1:
                years_contributing = 1  # At least 1 year if account exists
        except Exception:
            years_contributing = 1  # Default to 1 year if parsing fails
    
    # Determine repository quality tier based on total stars
    total_stars = data.get("total_stars", 0)
    if total_stars >= 1000:
        repo_tier = "Legend"
        tier_color = "#FFD700"  # Gold
    elif total_stars >= 100:
        repo_tier = "Pro"
        tier_color = "#C0C0C0"  # Silver
    else:
        repo_tier = "Newcomer"
        tier_color = "#CD7F32"  # Bronze
    
    dwg, theme = create_svg_base(theme_name, custom_colors, width, height, f"{data['username']}'s Trophy")
    
    font_family = theme["font_family"]
    text_color = theme["text_color"]
    title_color = theme["title_color"]
    icon_color = theme["icon_color"]
    
    # Trophy icon (left side)
    trophy_x = 80
    trophy_y = 120
    
    # Trophy base
    dwg.add(dwg.rect(insert=(trophy_x - 25, trophy_y + 30), size=(50, 10), 
                     fill=icon_color, rx=3, ry=3))
    dwg.add(dwg.rect(insert=(trophy_x - 10, trophy_y + 20), size=(20, 12), 
                     fill=icon_color, rx=2, ry=2))
    
    # Trophy cup
    dwg.add(dwg.path(d=f"M {trophy_x - 22} {trophy_y + 20} " \
                       f"L {trophy_x - 18} {trophy_y - 10} " \
                       f"L {trophy_x + 18} {trophy_y - 10} " \
                       f"L {trophy_x + 22} {trophy_y + 20} Z", 
                     fill=icon_color, opacity=0.9))
    
    # Trophy handles
    dwg.add(dwg.path(d=f"M {trophy_x - 18} {trophy_y} " \
                       f"Q {trophy_x - 35} {trophy_y - 5} {trophy_x - 30} {trophy_y + 15}", 
                     fill="none", stroke=icon_color, stroke_width=3))
    dwg.add(dwg.path(d=f"M {trophy_x + 18} {trophy_y} " \
                       f"Q {trophy_x + 35} {trophy_y - 5} {trophy_x + 30} {trophy_y + 15}", 
                     fill="none", stroke=icon_color, stroke_width=3))
    
    # Star on trophy
    star_x = trophy_x
    star_y = trophy_y - 5
    star_path = f"M {star_x} {star_y - 10} " \
                f"L {star_x + 2.5} {star_y - 3} " \
                f"L {star_x + 8} {star_y - 2} " \
                f"L {star_x + 4} {star_y + 3} " \
                f"L {star_x + 5} {star_y + 9} " \
                f"L {star_x} {star_y + 5} " \
                f"L {star_x - 5} {star_y + 9} " \
                f"L {star_x - 4} {star_y + 3} " \
                f"L {star_x - 8} {star_y - 2} " \
                f"L {star_x - 2.5} {star_y - 3} Z"
    dwg.add(dwg.path(d=star_path, fill=tier_color))
    
    # Stats section (right side)
    start_x = 180
    start_y = 80
    item_height = 50
    
    # Total Stars
    dwg.add(dwg.text("Total Stars", insert=(start_x, start_y + 15), 
                     fill=text_color, font_size=12, font_family=font_family))
    dwg.add(dwg.text(f"⭐ {total_stars:,}", insert=(start_x, start_y + 35), 
                     fill=title_color, font_size=18, font_family=font_family, font_weight="bold"))
    
    # Total Forks
    dwg.add(dwg.text("Total Forks", insert=(start_x, start_y + item_height + 15), 
                     fill=text_color, font_size=12, font_family=font_family))
    dwg.add(dwg.text(f"🔱 {total_forks:,}", insert=(start_x, start_y + item_height + 35), 
                     fill=title_color, font_size=18, font_family=font_family, font_weight="bold"))
    
    # Followers
    dwg.add(dwg.text("Followers", insert=(start_x, start_y + (item_height * 2) + 15), 
                     fill=text_color, font_size=12, font_family=font_family))
    dwg.add(dwg.text(f"👥 {data.get('followers', 0):,}", insert=(start_x, start_y + (item_height * 2) + 35), 
                     fill=title_color, font_size=18, font_family=font_family, font_weight="bold"))
    
    # Years Contributing
    dwg.add(dwg.text("Years Contributing", insert=(start_x, start_y + (item_height * 3) + 15), 
                     fill=text_color, font_size=12, font_family=font_family))
    dwg.add(dwg.text(f"📅 {years_contributing} year{'s' if years_contributing != 1 else ''}", 
                     insert=(start_x, start_y + (item_height * 3) + 35), 
                     fill=title_color, font_size=18, font_family=font_family, font_weight="bold"))
    
    # Repository Quality Tier Badge (bottom center)
    badge_y = height - 45
    badge_width = 120
    badge_height = 35
    badge_x = (width - badge_width) // 2
    
    # Badge background with glow effect
    dwg.add(dwg.rect(insert=(badge_x, badge_y), size=(badge_width, badge_height), 
                     rx=8, ry=8, fill=theme["bg_color"], 
                     stroke=tier_color, stroke_width=2))
    
    # Badge text
    dwg.add(dwg.text(f"🏆 {repo_tier} Repository", 
                     insert=(width/2, badge_y + 23), 
                     fill=tier_color, font_size=14, font_family=font_family, 
                     text_anchor="middle", font_weight="bold"))
    
    # Divider line
    dwg.add(dwg.line(start=(20, height - 60), end=(width - 20, height - 60), 
                     stroke=theme.get("border_color", "#333"), 
                     stroke_width=1, opacity=0.3))
    
    # Total repositories info
    dwg.add(dwg.text(f"Public Repos: {data.get('public_repos', 0)}", 
                     insert=(width/2, height - 70), 
                     fill=text_color, font_size=11, font_family=font_family, 
                     text_anchor="middle", opacity=0.8))
    
    return dwg.tostring()
