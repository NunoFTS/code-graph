from backend.src.graph.graph import build_graph


def main():
    app = build_graph()

    result = app.invoke({
        "input": "Write a python function that prints the first 5 fibonacci numbers",
        "attempts": 0,
        "max_attempts": 3
    })

    print("\n=== FINAL RESULT ===")
    print(result)


if __name__ == "__main__":
    main()