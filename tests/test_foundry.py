import openai
from foundry_local_sdk import Configuration, FoundryLocalManager

MODEL_ALIAS = "phi-3.5-mini"
PROMPT = "Hello, world"


def main():
    config = Configuration(app_name="local_rag_assistant")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    manager.download_and_register_eps()

    model = manager.catalog.get_model(MODEL_ALIAS)
    model.download(
        lambda progress: print(f"\rDownloading model: {progress:.2f}%", end="", flush=True)
    )
    print()
    model.load()
    print("Model loaded.")

    manager.start_web_service()
    base_url = f"{manager.urls[0]}/v1"

    client = openai.OpenAI(base_url=base_url, api_key="none")

    response = client.chat.completions.create(
        model=model.id,
        messages=[{"role": "user", "content": PROMPT}],
    )
    print(response.choices[0].message.content)

    model.unload()
    manager.stop_web_service()


if __name__ == "__main__":
    main()
