import requests
from datetime import datetime, timedelta

def calculate_streaks(contributions):
    """
    Calculate current and longest streak from contribution data.
    contributions: list of dicts with 'date' and 'count' keys
    Returns: dict with current_streak, longest_streak, total_contributions
    """
    if not contributions:
        return {"current_streak": 0, "longest_streak": 0, "total_contributions": 0}
    
    # Sort by date
    sorted_contribs = sorted(contributions, key=lambda x: x.get('date', ''), reverse=True)
    
    total_contributions = sum(d.get('count', 0) for d in contributions)
    
    # Calculate current streak (from today backwards)
    current_streak = 0
    today = datetime.now().date()
    
    for contrib in sorted_contribs:
        date_str = contrib.get('date', '')
        if not date_str:
            continue
        try:
            contrib_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            continue
        
        # Check if this is today or within the streak
        days_diff = (today - contrib_date).days
        
        if days_diff == current_streak and contrib.get('count', 0) > 0:
            current_streak += 1
        elif days_diff == current_streak and contrib.get('count', 0) == 0:
            # Streak broken at today
            break
        elif days_diff > current_streak:
            # Gap in dates, check if we should continue
            if days_diff == current_streak + 1 and contrib.get('count', 0) > 0:
                current_streak += 1
            else:
                break
    
    # Calculate longest streak
    longest_streak = 0
    current_longest = 0
    
    # Sort chronologically for longest streak calculation
    chronological = sorted(contributions, key=lambda x: x.get('date', ''))
    
    for contrib in chronological:
        if contrib.get('count', 0) > 0:
            current_longest += 1
            longest_streak = max(longest_streak, current_longest)
        else:
            current_longest = 0
    
    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_contributions": total_contributions
    }

def get_top_repositories(username, sort_by="stars", limit=5):
    """
    Fetches top repositories for a user sorted by specified criteria.
    
    Args:
        username: GitHub username
        sort_by: Sort criteria - "stars", "forks", or "updated"
        limit: Number of repos to return (3, 5, or 10)
    
    Returns:
        List of dicts with repo data: name, description, language, stars, forks, updated_at
    """
    try:
        # Map sort criteria to GitHub API sort parameter
        sort_param = sort_by if sort_by in ["stars", "forks", "updated"] else "stars"
        
        # Fetch repos sorted by the criteria (GitHub API supports sorting)
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&type=owner&sort={sort_param}&direction=desc"
        repos_resp = requests.get(repos_url)
        
        if repos_resp.status_code != 200:
            return []
        
        repos_data = repos_resp.json()
        
        # Sort manually if needed (GitHub API sort might not work perfectly for all cases)
        if sort_param == "stars":
            repos_data.sort(key=lambda x: x.get("stargazers_count", 0), reverse=True)
        elif sort_param == "forks":
            repos_data.sort(key=lambda x: x.get("forks_count", 0), reverse=True)
        elif sort_param == "updated":
            repos_data.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        # Limit results
        top_repos = repos_data[:limit]
        
        # Extract relevant data
        result = []
        for repo in top_repos:
            result.append({
                "name": repo.get("name", "Unknown"),
                "description": repo.get("description", "") or "No description",
                "language": repo.get("language", "Unknown") or "Unknown",
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "updated_at": repo.get("updated_at", ""),
                "html_url": repo.get("html_url", "")
            })
        
        return result
        
    except Exception as e:
        print(f"Error fetching top repos: {e}")
        return []

def get_live_github_data(username):


    """
    Fetches real data from GitHub API. 
    Notes: 
    - Unauthenticated requests are rate-limited (60/hr).
    - For a real production app, we need a token or use GraphQL.
    - For this MVP, we scrape or use public endpoints where possible to avoid token complexity for the user usage.
    """
    try:
        # User details
        user_url = f"https://api.github.com/users/{username}"
        user_resp = requests.get(user_url)
        if user_resp.status_code != 200:
            return None
        user_data = user_resp.json()
        
        # Repos for stars count (limited to first 100 public repos for basic sum without pagination for MVP speed)
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&type=owner"
        repos_resp = requests.get(repos_url)
        repos_data = repos_resp.json() if repos_resp.status_code == 200 else []
        
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos_data)
        
        # Languages (Approximation from top repos)
        languages = {}
        for repo in repos_data[:10]: # Check top 10 repos
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Try to get Total Commits/Contributions via 3rd party API
        total_commits = "N/A"
        streak_data = {"current_streak": 0, "longest_streak": 0, "total_contributions": 0}
        try:
            contrib_url = f"https://github-contributions-api.jogruber.de/v4/{username}"
            contrib_resp = requests.get(contrib_url)
            if contrib_resp.status_code == 200:
                c_data = contrib_resp.json()
                # Sum up all contributions in the returned calendar year(s)
                all_days = []
                if 'contributions' in c_data:
                    for year_group in c_data['contributions']:
                        all_days.extend(year_group.get('days', []))
                    total_commits = sum(d.get('count', 0) for d in all_days)
                    # Calculate streaks
                    streak_data = calculate_streaks(all_days)
        except Exception as ex:
            print(f"Contrib API Error: {ex}")

        return {
            "username": username,
            "total_stars": total_stars,
            "total_commits": total_commits,
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "top_languages": top_langs,
            "streak_data": streak_data
        }

            
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_mock_data(username):
    """Returns dummy data for layout testing/building without hitting API limits"""
    return {
        "username": username,
        "total_stars": 120,
        "total_commits": 450,
        "public_repos": 25,
        "followers": 85,
        "top_languages": [("Python", 10), ("JavaScript", 5), ("Rust", 2)],
        "streak_data": {
            "current_streak": 15,
            "longest_streak": 45,
            "total_contributions": 450
        }
    }
