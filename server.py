import asyncio
from mcp.server.fastmcp import FastMCP
from app import create_graphical_abstract_from_url, create_graphical_abstract

mcp = FastMCP("jama-abstract-generator")

@mcp.tool()
async def generate_graphical_abstract(url: str, github_repo: str | None = None, github_token: str | None = None) -> str:
    """
    URL'den PPTX üretir. Eğer `github_repo` (kullanici/repoadi) ve `github_token` verilirse,
    dosyayı `latest-abstract` release'ine yükler ve indirme linkini döndürür.
    """
    loop = asyncio.get_event_loop()
    if github_repo and github_token:
        return await loop.run_in_executor(
            None,
            create_graphical_abstract,
            url,
            github_repo,
            github_token,
        )
    # Geriye dönük uyumluluk: sadece URL ile çalıştırma
    return await loop.run_in_executor(
        None,
        create_graphical_abstract_from_url,
        url,
    )

if __name__ == "__main__":
    mcp.run()