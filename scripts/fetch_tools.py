import requests
import json
import os
from datetime import datetime

TOKEN = os.environ.get("PH_TOKEN", "")

QUERY = """
{
  posts(first: 50, topic: "artificial-intelligence", order: VOTES) {
    edges {
      node {
        id
        name
        tagline
        description
        url
        votesCount
        reviewsRating
        reviewsCount
        website
        thumbnail { url }
        topics {
          edges {
            node { name }
          }
        }
      }
    }
  }
}
"""

def fetch():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    resp = requests.post(
        "https://api.producthunt.com/v2/api/graphql",
        headers=headers,
        json={"query": QUERY},
        timeout=30
    )
    data = resp.json()
    tools = []
    edges = data.get("data", {}).get("posts", {}).get("edges", [])
    for i, edge in enumerate(edges):
        node = edge["node"]
        topics = [t["node"]["name"] for t in node.get("topics", {}).get("edges", [])]
        category = topics[0] if topics else "AI Tool"
        tagline = node.get("tagline") or ""
        tools.append({
            "rank": i + 1,
            "id": node["id"],
            "name": node["name"],
            "tagline": tagline,
            "description": node.get("description") or tagline,
            "url": node.get("website") or node["url"],
            "ph_url": node["url"],
            "votes": node.get("votesCount") or 0,
            "rating": round(node.get("reviewsRating") or 4.5, 1),
            "reviews": node.get("reviewsCount") or 0,
            "thumbnail": node.get("thumbnail", {}).get("url") or "",
            "category": category,
            "tags": topics[:3] if topics else ["AI Tool"],
            "featured": i < 5,
            "updated": datetime.utcnow().strftime("%Y-%m-%d")
        })
    output = {
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "total": len(tools),
        "tools": tools
    }
    os.makedirs("data", exist_ok=True)
    with open("data/tools.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Fetched {len(tools)} tools")

if __name__ == "__main__":
    fetch()
