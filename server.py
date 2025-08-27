import os
import re
import asyncio
from typing import Optional
from fastmcp import FastMCP   # <— BURASI değişti: mcp.server.fastmcp değil
from app import create_graphical_abstract_from_url, create_graphical_abstract

mcp = FastMCP("jama-abstract-generator")

_JAMA_URL_RE = re.compile(r"^https://jamanetwork\.com/.*")

@mcp.tool()
async def generate_graphical_abstract(
    url: str,
    github_repo: Optional[str] = None,
    github_token: Optional[str] = None
) -> str:
    if not _JAMA_URL_RE.match(url):
        raise ValueError("URL JAMA Network alan adında olmalı: https://jamanetwork.com/...")

    repo = github_repo or os.getenv("GITHUB_REPO")
    token = github_token or os.getenv("GITHUB_TOKEN")

    try:
        if repo and token:
            return await asyncio.to_thread(create_graphical_abstract, url, repo, token)
        return await asyncio.to_thread(create_graphical_abstract_from_url, url)
    except Exception as e:
        return f"İşlem başarısız: {type(e).__name__}: {e}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    # FastMCP 2.x dokümantasyonuna göre HTTP böyle başlatılır
    mcp.run(transport="http", host="0.0.0.0", port=port)  # /mcp yolu otomatik
