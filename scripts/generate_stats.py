import os
import requests
import sys

def get_stats(token, username):
    headers = {"Authorization": f"Bearer {token}"}
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          totalCommitContributions
        }
        pullRequests(first: 1) {
          totalCount
        }
        issues(first: 1) {
          totalCount
        }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          nodes {
            stargazerCount
          }
        }
      }
    }
    """
    variables = {"login": username}
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Error fetching stats: {response.text}")
        sys.exit(1)
        
    data = response.json()
    if "errors" in data:
        print(f"GraphQL Error: {data['errors']}")
        sys.exit(1)
        
    user = data["data"]["user"]
    total_commits = user["contributionsCollection"]["totalCommitContributions"]
    total_prs = user["pullRequests"]["totalCount"]
    total_issues = user["issues"]["totalCount"]
    total_stars = sum(repo["stargazerCount"] for repo in user["repositories"]["nodes"])
    
    return {
        "commits": total_commits,
        "prs": total_prs,
        "issues": total_issues,
        "stars": total_stars
    }

def generate_svg(stats):
    # Dark theme colors
    bg_color = "#0d1117"
    text_color = "#c9d1d9"
    accent_color = "#58a6ff"
    border_color = "#30363d"
    
    svg_content = f"""
    <svg width="400" height="180" viewBox="0 0 400 180" xmlns="http://www.w3.org/2000/svg">
      <style>
        .header {{ font: 600 18px 'Segoe UI', Ubuntu, Sans-Serif; fill: {accent_color}; }}
        .stat {{ font: 600 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: {text_color}; }}
        .value {{ font: 400 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: {text_color}; }}
        .box {{ fill: {bg_color}; stroke: {border_color}; stroke-width: 1px; rx: 4px; }}
      </style>
      <rect x="1" y="1" width="398" height="178" class="box"/>
      <text x="20" y="35" class="header">GitHub Statistics</text>
      
      <g transform="translate(20, 65)">
        <text x="0" y="0" class="stat">Total Commits:</text>
        <text x="120" y="0" class="value">{stats['commits']}</text>
      </g>
      
      <g transform="translate(20, 95)">
        <text x="0" y="0" class="stat">Pull Requests:</text>
        <text x="120" y="0" class="value">{stats['prs']}</text>
      </g>
      
      <g transform="translate(20, 125)">
        <text x="0" y="0" class="stat">Issues Opened:</text>
        <text x="120" y="0" class="value">{stats['issues']}</text>
      </g>
      
      <g transform="translate(20, 155)">
        <text x="0" y="0" class="stat">Stars Earned:</text>
        <text x="120" y="0" class="value">{stats['stars']}</text>
      </g>
      
      <!-- Decorative IoT/CS Element -->
      <path d="M250 60 L350 60 L350 140 L250 140 Z" fill="none" stroke="{border_color}" stroke-width="2"/>
      <circle cx="270" cy="80" r="5" fill="{accent_color}"/>
      <circle cx="330" cy="80" r="5" fill="{accent_color}"/>
      <circle cx="270" cy="120" r="5" fill="{accent_color}"/>
      <circle cx="330" cy="120" r="5" fill="{accent_color}"/>
      <path d="M270 80 L330 120 M330 80 L270 120" stroke="{accent_color}" stroke-width="1" opacity="0.5"/>
    </svg>
    """
    return svg_content

def main():
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    
    if not token or not repo:
        print("Missing GITHUB_TOKEN or GITHUB_REPOSITORY env vars")
        sys.exit(1)
        
    username = repo.split("/")[0]
    
    print(f"Fetching stats for {username}...")
    stats = get_stats(token, username)
    print(f"Stats: {stats}")
    
    svg = generate_svg(stats)
    
    output_path = "assets/stats.svg"
    os.makedirs("assets", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(svg)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    main()
