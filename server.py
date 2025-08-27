import os
import re
import asyncio
from typing import Optional
from mcp.server.fastmcp import FastMCP
from app import create_graphical_abstract_from_url, create_graphical_abstract

mcp = FastMCP("jama-abstract-generator")  # host/port'u run()'a DEĞİL, env'e vereceğiz

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
    # Smithery container PORT verir (örn. 8000). Bunu FastMCP'nin beklediği env'e köprüleyelim.
    port = os.environ.get("PORT", "8000")
    os.environ.setdefault("FASTMCP_HOST", "0.0.0.0")
    os.environ["FASTMCP_PORT"] = str(port)
    # Streamable HTTP için run()'ı basit çağır
    mcp.run(transport="http")  # host/port burada verilmez
