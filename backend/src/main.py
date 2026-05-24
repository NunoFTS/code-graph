from backend.src.graph.graph import build_graph


def main():
    app = build_graph()

    result = app.invoke({
        "input": "Write a Python function that adds two numbers"
    })

    print("\n=== FINAL RESULT ===")
    print(result)


if __name__ == "__main__":
    main()