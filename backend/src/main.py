import logging

from backend.src.agents.factory import AgentFactory
from backend.src.config.errors import ConfigError
from backend.src.config.settings import AppSettings
from backend.src.graph.graph import build_graph
from backend.src.utils.logging_setup import configure_logging


def main():
    try:
        settings = AppSettings.load()
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        raise SystemExit(2) from exc

    run_id = configure_logging(logs_dir=settings.logs_dir, testing=settings.testing)

    logger = logging.getLogger(__name__)
    logger.info("app_start", extra={"event": "app_start", "run_id": run_id, "testing": settings.testing})

    factory = AgentFactory.from_settings(settings)
    app = build_graph(factory)

    result = app.invoke({
        "input": "Write a python function that prints the first 5 fibonacci numbers",
        "attempts": 0,
        "max_attempts": 3
    })

    logger.info("app_done", extra={"event": "app_done", "run_id": run_id})
    print("\n=== FINAL RESULT ===")
    print(result)


if __name__ == "__main__":
    main()
