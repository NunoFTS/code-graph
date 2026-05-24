from backend.src.graph.graph import build_graph


def main():
    app = build_graph()

    initial_state = {
        "input": "Write a Python function that adds two numbers",
        "attempts": 0,
        "max_attempts": 3
    }

    result = app.invoke(initial_state)

    print("\n=== FINAL RESULT ===")
    print(f"Input: {result.get('input')}")
    print(f"Generated Code:\n{result.get('generated_code')}")
    print(f"Validation Result: {result.get('validation_result')}")
    print(f"Is Valid: {result.get('is_valid')}")
    print(f"Attempts: {result.get('attempts')}/{result.get('max_attempts')}")


if __name__ == "__main__":
    main()
