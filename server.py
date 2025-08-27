import os
import re
import asyncio
from typing import Optional
from mcp.server.fastmcp import FastMCP
from app import create_graphical_abstract_from_url, create_graphical_abstract

# MCP sunucu adı
mcp = FastMCP("jama-abstract-generator")

# JAMA URL doğrulama regex'i
_JAMA_URL_RE = re.compile(r"^https://jamanetwork\.com/.*")

@mcp.tool()
async def generate_graphical_abstract(
    url: str,
    github_repo: Optional[str] = None,
    github_token: Optional[str] = None
) -> str:
    """
    Verilen JAMA makale URL'sinden PPTX üretir.
    Eğer `github_repo` (kullanici/repoadi) ve `github_token` sağlanırsa,
    dosyayı 'latest-abstract' release'ine yükler ve indirme linkini döndürür.

    Not: `github_repo` / `github_token` parametre gönderilmezse
    GITHUB_REPO / GITHUB_TOKEN ortam değişkenlerinden okunur.
    """

    if not _JAMA_URL_RE.match(url):
        raise ValueError("URL JAMA Network alan adında olmalı: https://jamanetwork.com/...")

    # Parametre yoksa env'den doldur
    repo = github_repo or os.getenv("GITHUB_REPO")
    token = github_token or os.getenv("GITHUB_TOKEN")

    try:
        if repo and token:
            # CPU-bound / I/O karışık işlemler için to_thread
            return await asyncio.to_thread(create_graphical_abstract, url, repo, token)

        # Geriye dönük: yalnızca URL ile çalıştır
        return await asyncio.to_thread(create_graphical_abstract_from_url, url)

    except Exception as e:
        # Araç çıktısı string olduğu için hatayı metinle döndürüyoruz
        return f"İşlem başarısız: {type(e).__name__}: {e}"

if __name__ == "__main__":
    # Smithery container runtime PORT'u env ile sağlar (örn. 8000)
    port = int(os.environ.get("PORT", "8000"))
    # Streamable HTTP transport
    mcp.run(transport="http", host="0.0.0.0", port=port, path="/mcp")
