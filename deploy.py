import asyncio
from gemini_webapi import GeminiClient

Secure_1PSID = "g.a000yQiY8-6KL3KoPHz24dsTZPu-klKLdN-rEBCIPlC9Y1SsvjByNLMmFKzOLDzdbdmJNue_hQACgYKAY0SARQSFQHGX2MipoicyZ7mKVTrFc8jzjrWShoVAUF8yKrCdqG2K00KhDqUxVmB1y8a0076"
Secure_1PSIDTS = "sidts-CjIB5H03PyfysfdWvxEtXEEBq57TjNxuDrRuctIQvMKAZnp5oWj0qHttIjRIKPxGkY0OghAA"

async def main():
    client = GeminiClient(Secure_1PSID, Secure_1PSIDTS, proxy=None)
    await client.init(timeout=30, auto_close=False, close_delay=300, auto_refresh=True)
    
    print("Gemini API client initialized successfully!")
    
    # Test the client
    response = await client.generate_content("Hello! Please confirm you're working.")
    print(f"\nTest response: {response.text}")

if __name__ == "__main__":
    asyncio.run(main())