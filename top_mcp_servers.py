import json
import os


def load_json_file(path, default_value):
    if not os.path.exists(path):
        return default_value
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def add_server(collector, server, source, server_type=None):
    url = server.get("url") or ""
    key = url.lower() if url else (server.get("name", "") + "|" + url)
    existing = collector.get(key, {})

    merged = {}
    merged["name"] = server.get("name") or existing.get("name")
    merged["url"] = url or existing.get("url")
    merged["description"] = server.get("description") or existing.get("description")
    merged["category"] = server.get("category") or existing.get("category")

    languages = server.get("languages")
    if languages is None:
        languages = existing.get("languages")
    merged["languages"] = languages or []

    scopes = server.get("scopes")
    if scopes is None:
        scopes = existing.get("scopes")
    merged["scopes"] = scopes or []

    platforms = server.get("platforms")
    if platforms is None:
        platforms = existing.get("platforms")
    merged["platforms"] = platforms or []

    is_official = server.get("is_official")
    if is_official is None:
        is_official = existing.get("is_official")
    if is_official is None and server_type in ("reference", "integration"):
        is_official = True
    merged["is_official"] = bool(is_official)

    if server.get("is_open_source") is not None:
        is_open_source = server.get("is_open_source")
    else:
        is_open_source = existing.get("is_open_source")
    merged["is_open_source"] = bool(is_open_source) if is_open_source is not None else False

    star = server.get("star_count")
    if star is None:
        star = existing.get("star_count")
    merged["star_count"] = star

    logo = server.get("logo") or existing.get("logo")
    if logo:
        merged["logo"] = logo

    merged["source"] = existing.get("source") or source
    merged["type"] = server_type or existing.get("type")

    collector[key] = merged


def build_top_servers(limit=100):
    awesome = load_json_file("awesome_mcp_servers.json", [])
    official = load_json_file(
        "mcp_official_servers.json",
        {"reference_servers": [], "third_party": {"official_integrations": [], "community_servers": []}},
    )

    combined = {}

    for s in awesome:
        add_server(combined, s, "awesome", None)

    for s in official.get("reference_servers", []):
        add_server(combined, s, "official", "reference")

    third_party = official.get("third_party", {}) or {}
    for s in third_party.get("official_integrations", []):
        add_server(combined, s, "official", "integration")
    for s in third_party.get("community_servers", []):
        add_server(combined, s, "official", "community")

    servers = [v for v in combined.values() if isinstance(v.get("star_count"), (int, float))]
    servers.sort(key=lambda x: x.get("star_count", 0), reverse=True)
    return servers[:limit]


def main():
    top_servers = build_top_servers(100)
    with open("mcp_top100_servers.json", "w", encoding="utf-8") as f:
        json.dump(top_servers, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(top_servers)} servers to mcp_top100_servers.json")


if __name__ == "__main__":
    main()

