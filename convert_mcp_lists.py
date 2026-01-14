import re
import json
import os
import requests
import time

def fetch_content(url):
    """Fetch content from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_github_stars(servers, token):
    """
    Fetch GitHub stars using GraphQL API in batches.
    Updates the servers list in-place with 'star_count'.
    """
    if not token:
        print("No GITHUB_TOKEN provided, skipping star count fetch.")
        return

    print("Fetching GitHub stars...")
    
    # Filter for GitHub URLs and extract owner/repo
    github_repos = {} # map "owner/repo" -> list of server objects
    # Regex to capture owner/repo from various github url formats
    # Supports: https://github.com/owner/repo, http://github.com/owner/repo, https://github.com/owner/repo/tree/...
    repo_pattern = re.compile(r'github\.com/([^/]+)/([^/]+)')
    
    for server in servers:
        url = server.get('url', '')
        if not url:
            continue
            
        match = repo_pattern.search(url)
        if match:
            owner, repo = match.group(1), match.group(2)
            # Remove .git suffix if present
            if repo.endswith('.git'):
                repo = repo[:-4]
            full_name = f"{owner}/{repo}"
            
            if full_name not in github_repos:
                github_repos[full_name] = []
            github_repos[full_name].append(server)

    # Prepare batches (GraphQL limits check to usually 100 nodes, sticking to 50-80 is safe)
    repo_names = list(github_repos.keys())
    batch_size = 80 
    
    api_url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json"
    }

    for i in range(0, len(repo_names), batch_size):
        batch = repo_names[i:i + batch_size]
        print(f"Fetching batch {i//batch_size + 1}/{(len(repo_names) + batch_size - 1)//batch_size} ({len(batch)} repos)...")
        
        # Build GraphQL query
        # alias: repository(owner: "...", name: "...") { stargazers { totalCount } }
        query_parts = []
        for idx, full_name in enumerate(batch):
            owner, repo = full_name.split('/', 1)
            # GraphQL aliases must be alphanumeric
            alias = f"repo_{idx}"
            query_parts.append(f'{alias}: repository(owner: "{owner}", name: "{repo}") {{ stargazers {{ totalCount }} }}')
            
        query = "query { " + " ".join(query_parts) + " }"
        
        try:
            response = requests.post(api_url, json={'query': query}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    # Partial errors can happen (e.g. repo deleted, renamed, or private)
                    # We just log and continue processing successful ones
                    print(f"  Note: GraphQL returned some errors (likely missing/private repos)")
                
                results = data.get('data', {})
                if results:
                    for idx, full_name in enumerate(batch):
                        alias = f"repo_{idx}"
                        repo_data = results.get(alias)
                        if repo_data and 'stargazers' in repo_data:
                            stars = repo_data['stargazers']['totalCount']
                            # Update all servers matching this repo
                            for server in github_repos[full_name]:
                                server['star_count'] = stars
            else:
                print(f"  Error: API returned {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"  Exception during batch fetch: {e}")
            
        # Slight delay to be nice to the API
        time.sleep(1)

def is_open_source_url(url):
    """
    Improved logic to detect if a URL points to an open source repository.
    Includes major hosting platforms and self-hosted instances.
    """
    if not url:
        return False
        
    url_lower = url.lower()
    
    # Common open source hosting platforms
    os_platforms = [
        'github.com',
        'gitlab.com',
        'gitea.com',
        'gitea.io',
        'bitbucket.org',
        'codeberg.org',
        'sourcehut.org',
        'sr.ht',
        'savannah.gnu.org',
        'git.sr.ht',
        'sourceforge.net',
        'launchpad.net'
    ]
    
    # Check if any platform is in the URL
    if any(platform in url_lower for platform in os_platforms):
        return True
        
    # Relative URLs in the official repo are considered open source (GitHub)
    if not url.startswith('http'):
        return True
        
    # Common self-hosted patterns
    self_hosted_patterns = [
        '/git/',
        'git.',
        'gitea.',
        'gitlab.'
    ]
    if any(pattern in url_lower for pattern in self_hosted_patterns):
        # Additional check to avoid false positives for just any "git" in domain
        # This is a heuristic and might need adjustment
        return True
        
    return False

def parse_awesome_mcp(content):
    lines = content.split('\n')

    servers = []
    current_category = ""
    
    # Icon mappings
    lang_icons = {
        '🐍': 'Python',
        '📇': 'TypeScript',
        '🏎️': 'Go',
        '🦀': 'Rust',
        '#️⃣': 'C#',
        '☕': 'Java',
        '🌊': 'C/C++',
        '💎': 'Ruby'
    }
    scope_icons = {
        '☁️': 'Cloud',
        '🏠': 'Local',
        '📟': 'Embedded'
    }
    os_icons = {
        '🍎': 'macOS',
        '🪟': 'Windows',
        '🐧': 'Linux'
    }
    
    # Pattern for list items: - [name](url) icons - description
    item_pattern = re.compile(r'^\s*-\s*\[([^\]]+)\]\(([^)]+)\)(.*)$')
    category_pattern = re.compile(r'^###\s+(?:.*?>)?([^<]+)(?:</a>)?.*$')

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for category
        cat_match = category_pattern.match(line)
        if cat_match:
            current_category = cat_match.group(1).strip()
            continue
            
        # Check for server item
        item_match = item_pattern.match(line)
        if item_match:
            name = item_match.group(1).strip()
            url = item_match.group(2).strip()
            rest = item_match.group(3).strip()
            
            # Extract icons and description
            description = ""
            if ' - ' in rest:
                icons_part, description = rest.split(' - ', 1)
            else:
                icons_part = rest
                description = "" # or look for first non-icon text
            
            languages = [lang_icons[icon] for icon in lang_icons if icon in icons_part]
            scopes = [scope_icons[icon] for icon in scope_icons if icon in icons_part]
            platforms = [os_icons[icon] for icon in os_icons if icon in icons_part]
            is_official = '🎖️' in icons_part
            is_open_source = is_open_source_url(url)
            
            servers.append({
                "name": name,
                "url": url,
                "description": description.strip(),
                "category": current_category,
                "languages": languages,
                "scopes": scopes,
                "platforms": platforms,
                "is_official": is_official,
                "is_open_source": is_open_source
            })
            
    return servers

def parse_official_mcp(content):
    data = {
        "reference_servers": [],
        "third_party": {
            "official_integrations": [],
            "community_servers": []
        }
    }

    # Extract Reference Servers
    ref_section = re.search(r'## 🌟 Reference Servers(.*?)(?=##|$)', content, re.S)
    if ref_section:
        items = re.findall(r'-\s+\*\*\[([^\]]+)\]\(([^)]+)\)\*\*\s+-\s+(.*?)(?=\n-|\n\n|$)', ref_section.group(1), re.S)
        for name, url, desc in items:
            is_open_source = is_open_source_url(url)
            full_url = url.strip()
            if not full_url.startswith('http'):
                full_url = f"https://github.com/modelcontextprotocol/servers/tree/main/{full_url}"
            
            data["reference_servers"].append({
                "name": name.strip(),
                "url": full_url,
                "description": desc.strip().replace('\n', ' '),
                "is_open_source": is_open_source
            })

    # Extract Third-Party - Official Integrations
    official_section = re.search(r'### 🎖️ Official Integrations(.*?)(?=###|$)', content, re.S)
    if official_section:
        # Pattern for items with logo: - <img ... src="logo_url" ... /> **[name](url)** - description
        # Also handle items without logo: - **[name](url)** - description
        items = re.findall(r'-\s+(?:<img[^>]+src="([^"]+)"[^>]*>\s+)?\*\*\[([^\]]+)\]\(([^)]+)\)\*\*(?:\s+—|\s+-)\s+(.*?)(?=\n-|\n\n|$)', official_section.group(1), re.S)
        for logo, name, url, desc in items:
            is_open_source = is_open_source_url(url)
            data["third_party"]["official_integrations"].append({
                "name": name.strip(),
                "url": url.strip(),
                "description": desc.strip().replace('\n', ' '),
                "logo": logo.strip() if logo else None,
                "is_open_source": is_open_source
            })

    # Extract Third-Party - Community Servers
    community_section = re.search(r'### 🌎 Community Servers(.*?)(?=##|$)', content, re.S)
    if community_section:
        items = re.findall(r'-\s+\*\*\[([^\]]+)\]\(([^)]+)\)\*\*\s+-\s+(.*?)(?=\n-|\n\n|$)', community_section.group(1), re.S)
        for name, url, desc in items:
            is_open_source = is_open_source_url(url)
            data["third_party"]["community_servers"].append({
                "name": name.strip(),
                "url": url.strip(),
                "description": desc.strip().replace('\n', ' '),
                "is_open_source": is_open_source
            })

    return data

def main():
    # Remote URLs
    awesome_url = 'https://raw.githubusercontent.com/punkpeye/awesome-mcp-servers/main/README.md'
    official_url = 'https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md'
    
    # 1. Process Awesome MCP Servers
    print("Processing Awesome MCP Servers...")
    awesome_content = fetch_content(awesome_url)
            
    if awesome_content:
        awesome_data = parse_awesome_mcp(awesome_content)
        # Note: We postpone saving until we fetch stars
    else:
        print("Skipping Awesome MCP update due to fetch failure")

    # 2. Process Official MCP Servers
    print("\nProcessing Official MCP Servers...")
    official_content = fetch_content(official_url)
            
    if official_content:
        official_data = parse_official_mcp(official_content)
        
        # Collect all servers from official list for star fetching
        official_all_servers = []
        official_all_servers.extend(official_data["reference_servers"])
        official_all_servers.extend(official_data["third_party"]["official_integrations"])
        official_all_servers.extend(official_data["third_party"]["community_servers"])
        
        # Combine with Awesome list for single batch processing to save requests
        # Note: We need to be careful if we want to fetch stars for both lists efficiently.
        # Actually, simpler to fetch separately or just pass a combined list of *objects* to the function.
        # The function modifies objects in-place, so we can pass a giant list.
        
        all_servers_to_fetch = []
        if 'awesome_data' in locals():
            all_servers_to_fetch.extend(awesome_data)
        all_servers_to_fetch.extend(official_all_servers)
        
        # Fetch stars for all collected servers
        token = os.environ.get("GITHUB_TOKEN")
        get_github_stars(all_servers_to_fetch, token)
        
        # Save Awesome data (now with stars)
        if 'awesome_data' in locals():
            with open('awesome_mcp_servers.json', 'w', encoding='utf-8') as f:
                json.dump(awesome_data, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(awesome_data)} servers to awesome_mcp_servers.json")

        # Save Official data (now with stars)
        with open('mcp_official_servers.json', 'w', encoding='utf-8') as f:
            json.dump(official_data, f, indent=2, ensure_ascii=False)
        print(f"Saved official servers to mcp_official_servers.json")
    else:
        print("Skipping Official MCP update due to fetch failure")

if __name__ == "__main__":
    main()
