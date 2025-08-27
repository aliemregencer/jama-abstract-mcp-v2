import os
import re
import asyncio
from typing import Optional
from fastmcp import FastMCP
from app import create_graphical_abstract_from_url, create_graphical_abstract

mcp = FastMCP("jama-va-abstract-generator")

_JAMA_URL_RE = re.compile(r"^https://jamanetwork\.com/.*")

@mcp.tool()
async def generate_va_abstract(
    url: str,
    github_repo: Optional[str] = None,
    github_token: Optional[str] = None
) -> str:
    """
    JAMA Network makalesinden VA (Veterans Affairs) formatında görsel özet oluşturur.
    Parametre verilmezse GITHUB_REPO / GITHUB_TOKEN ortam değişkenlerinden okunur.
    """
    if not _JAMA_URL_RE.match(url):
        raise ValueError("URL JAMA Network alan adında olmalı: https://jamanetwork.com/...")

    repo = github_repo or os.getenv("GITHUB_REPO")
    token = github_token or os.getenv("GITHUB_TOKEN")

    try:
        if repo and token:
            print("VA formatında özet oluşturuluyor ve GitHub'a yükleniyor...")
            return await asyncio.to_thread(create_graphical_abstract, url, repo, token)
        else:
            print("VA formatında özet oluşturuluyor (GitHub yükleme olmadan)...")
            return await asyncio.to_thread(create_graphical_abstract_from_url, url)
    except Exception as e:
        error_msg = f"İşlem başarısız: {type(e).__name__}: {e}"
        print(error_msg)
        return error_msg

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print("JAMA VA Abstract Generator MCP Server başlatılıyor...")
    print(f"Port: {port}")
    print(f"Template: templates/jama_va.pptx")
    print(f"Endpoint: http://localhost:{port}")  # path vermiyorsak kök uç nokta

    # FastMCP 2.x: HTTP böyle başlatılır (fastmcp paketinden import şart)
    mcp.run(transport="http", host="0.0.0.0", port=port)
