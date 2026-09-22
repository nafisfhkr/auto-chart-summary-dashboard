import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.config.settings import get_llm_settings
from app.providers.factory import create_llm_provider


def main() -> None:
    settings = get_llm_settings()
    provider = create_llm_provider(settings)
    response = provider.generate(
        [
            {
                "role": "user",
                "content": "Jawab singkat: sebutkan ibu kota Jawa Timur.",
            }
        ]
    )

    print("Model:", settings.model)
    print("Response:")
    print(response)


if __name__ == "__main__":
    main()
