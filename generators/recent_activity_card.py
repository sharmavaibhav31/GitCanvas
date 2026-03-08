import svgwrite
import requests
from themes.styles import THEMES
from utils.rate_limiter import make_github_request, get_rate_limit_status
import logging

logger = logging.getLogger(__name__)


def draw_recent_activity_card(data, theme_name="Default", custom_colors=None, token=None):
    """
    Fetches the user's GitHub events and renders a simple text-based SVG
    showing the last 3 Pull Request or Issue events.

    Params:
      data: dict with at least 'username'
      theme_name: string key from THEMES OR a theme dictionary (if already resolved)
      custom_colors: dict to override theme values (only used if theme_name is a string)
      token: optional GitHub token string for higher rate limit

    Returns: SVG string
    """
    username = data.get('username')
    if not username:
        raise ValueError("data must include 'username'")

    # FIXED: Handle both string theme name and pre-resolved theme dict
    if isinstance(theme_name, dict):
        # Already a theme dictionary (e.g., current_theme_opts from app.py)
        theme = theme_name.copy()
    else:
        # Convert theme_name string to actual theme dictionary
        theme = THEMES.get(theme_name, THEMES["Default"]).copy()
        
        # Apply custom colors if provided
        if custom_colors:
            theme.update(custom_colors)

    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    url = f"https://api.github.com/users/{username}/events"
    
    # Check rate limit status before making request
    rate_limit = get_rate_limit_status()
    if rate_limit and rate_limit.should_wait(threshold=2):
        wait_time = rate_limit.time_until_reset()
        if wait_time > 60:  # Don't wait more than 1 minute for activity card
            logger.warning(f"Rate limit low, skipping recent activity (would wait {wait_time:.1f}s)")
            return _render_svg_lines(["Rate limit reached - try again later"], theme)
    
    # Make rate-limited request
    resp = make_github_request(url, headers=headers, timeout=8)
    
    if not resp:
        logger.error("Failed to fetch events after retries")
        return _render_svg_lines(["Error fetching recent activity"], theme)

    if resp.status_code != 200:
        logger.error(f"GitHub API error: {resp.status_code}")
        if resp.status_code == 429:
            return _render_svg_lines(["Rate limit reached - try again later"], theme)
        else:
            return _render_svg_lines([f"GitHub API error: {resp.status_code}"], theme)

    try:
        events = resp.json()
    except ValueError as e:
        logger.error(f"Invalid JSON in events response: {e}")
        return _render_svg_lines(["Error: Invalid response format"], theme)

    if not isinstance(events, list):
        logger.error(f"Expected list of events, got {type(events)}")
        return _render_svg_lines(["Error: Unexpected response format"], theme)

    lines = []
    for ev in events:
        if not isinstance(ev, dict):
            continue
            
        event_type = ev.get('type', '')
        
        if event_type == 'PullRequestEvent':
            payload = ev.get('payload', {})
            action = payload.get('action', '')
            pr = payload.get('pull_request', {})
            number = pr.get('number', 0)
            title = pr.get('title', '')[:100]  # Truncate long titles
            repo_data = ev.get('repo', {})
            repo = repo_data.get('name', '')[:50]  # Truncate long repo names
            merged = pr.get('merged', False)

            if merged:
                lines.append(f"Merged PR #{number} in {repo}: {title}")
            else:
                if action == 'opened':
                    lines.append(f"Opened PR #{number} in {repo}: {title}")
                elif action == 'closed':
                    lines.append(f"Closed PR #{number} in {repo}: {title}")
                else:
                    lines.append(f"PR #{number} {action} in {repo}: {title}")

        elif event_type == 'IssuesEvent':
            payload = ev.get('payload', {})
            action = payload.get('action', '')
            issue = payload.get('issue', {})
            number = issue.get('number', 0)
            title = issue.get('title', '')[:100]  # Truncate long titles
            repo_data = ev.get('repo', {})
            repo = repo_data.get('name', '')[:50]  # Truncate long repo names

            if action == 'opened':
                lines.append(f"Opened Issue #{number} in {repo}: {title}")
            elif action == 'closed':
                lines.append(f"Closed Issue #{number} in {repo}: {title}")
            else:
                lines.append(f"Issue #{number} {action} in {repo}: {title}")

        if len(lines) >= 3:
            break

    if not lines:
        lines = ["No recent PRs or Issues found."]

    return _render_svg_lines(lines[:3], theme)


def _render_svg_lines(lines, theme):
    width = 520
    height = 120
    dwg = svgwrite.Drawing(size=("100%", "100%"), viewBox=f"0 0 {width} {height}")

    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), rx=8, ry=8,
                     fill=theme["bg_color"], stroke=theme["border_color"], stroke_width=2))

    title = "Recent Activity"
    dwg.add(dwg.text(title, insert=(20, 30),
                     fill=theme["title_color"], font_size=theme.get("title_font_size", 18),
                     font_family=theme.get("font_family", "sans-serif"), font_weight="bold"))

    y = 55
    for i, line in enumerate(lines):
        # simple truncation to avoid overflow
        text = line if len(line) <= 80 else line[:77] + '...'
        dwg.add(dwg.text(text, insert=(20, y + i * 20),
                         fill=theme["text_color"], font_size=theme.get("text_font_size", 14),
                         font_family=theme.get("font_family", "sans-serif")))

    return dwg.tostring()