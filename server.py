import asyncio
from mcp.server.fastmcp import FastMCP
from app import create_graphical_abstract_from_url

mcp = FastMCP("jama-abstract-generator")

@mcp.tool()
async def generate_graphical_abstract(url: str) -> str:
    """
    Bir JAMA Network Open makale URL'si alır ve makalenin görsel özetini
    içeren bir PowerPoint (PPTX) dosyası oluşturur.
    Başarılı olduğunda oluşturulan dosyanın adını döndürür.
    """
    # Scraping ve dosya oluşturma işlemleri zaman alıcı ve senkron işlemlerdir.
    # Bu nedenle, asenkron sunucuyu bloke etmemek için ayrı bir thread'de çalıştırırız.
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,  # Varsayılan thread pool executor'ı kullanır
        create_graphical_abstract_from_url, # Çalıştırılacak fonksiyon
        url    # Fonksiyona verilecek argüman
    )
    return result

if __name__ == "__main__":
    mcp.run()