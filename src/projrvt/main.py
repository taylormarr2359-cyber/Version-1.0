from .assistant import AtlasAssistant


def hello(name: str = "world") -> str:
    return f"Hello, {name}!"


def run_cli() -> None:
    assistant = AtlasAssistant()
    wake_word = "atlas"

    print("ATLAS online. Type 'exit' to quit.")
    print(f"Wake word is '{wake_word}'. Example: atlas help me plan my day")
    print("Commands: weather <city>, calendar, email, notes, smart home")

    while True:
        user_input = input("\nYou> ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("ATLAS shutting down.")
            break

        text = user_input
        lowered = user_input.lower()

        # Wake-word mode (if included, strip it and process)
        if lowered.startswith(wake_word + " "):
            text = user_input[len(wake_word) + 1 :].strip()

        result = assistant.handle(text, speak=False)
        print(f"ATLAS> {result.text}")


if __name__ == "__main__":
    run_cli()
