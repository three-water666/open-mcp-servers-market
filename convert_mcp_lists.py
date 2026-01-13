import re
import json
import os

def parse_awesome_mcp(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

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
            
            servers.append({
                "name": name,
                "url": url,
                "description": description.strip(),
                "category": current_category,
                "languages": languages,
                "scopes": scopes,
                "platforms": platforms,
                "is_official": is_official
            })
            
    return servers

def parse_official_mcp(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

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
            data["reference_servers"].append({
                "name": name.strip(),
                "url": url.strip(),
                "description": desc.strip().replace('\n', ' ')
            })

    # Extract Third-Party - Official Integrations
    official_section = re.search(r'### 🎖️ Official Integrations(.*?)(?=###|$)', content, re.S)
    if official_section:
        # Pattern for items with logo: - <img ... src="logo_url" ... /> **[name](url)** - description
        # Also handle items without logo: - **[name](url)** - description
        items = re.findall(r'-\s+(?:<img[^>]+src="([^"]+)"[^>]*>\s+)?\*\*\[([^\]]+)\]\(([^)]+)\)\*\*(?:\s+—|\s+-)\s+(.*?)(?=\n-|\n\n|$)', official_section.group(1), re.S)
        for logo, name, url, desc in items:
            data["third_party"]["official_integrations"].append({
                "name": name.strip(),
                "url": url.strip(),
                "description": desc.strip().replace('\n', ' '),
                "logo": logo.strip() if logo else None
            })

    # Extract Third-Party - Community Servers
    community_section = re.search(r'### 🌎 Community Servers(.*?)(?=##|$)', content, re.S)
    if community_section:
        items = re.findall(r'-\s+\*\*\[([^\]]+)\]\(([^)]+)\)\*\*\s+-\s+(.*?)(?=\n-|\n\n|$)', community_section.group(1), re.S)
        for name, url, desc in items:
            data["third_party"]["community_servers"].append({
                "name": name.strip(),
                "url": url.strip(),
                "description": desc.strip().replace('\n', ' ')
            })

    return data

def main():
    awesome_file = 'awesome-mcp-servers.md'
    official_file = 'modelcontextprotocol-servers.md'
    
    if os.path.exists(awesome_file):
        print(f"Parsing {awesome_file}...")
        awesome_data = parse_awesome_mcp(awesome_file)
        with open('awesome_mcp_servers.json', 'w', encoding='utf-8') as f:
            json.dump(awesome_data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(awesome_data)} servers to awesome_mcp_servers.json")

    if os.path.exists(official_file):
        print(f"Parsing {official_file}...")
        official_data = parse_official_mcp(official_file)
        with open('mcp_official_servers.json', 'w', encoding='utf-8') as f:
            json.dump(official_data, f, indent=2, ensure_ascii=False)
        print(f"Saved official servers to mcp_official_servers.json")

if __name__ == "__main__":
    main()
