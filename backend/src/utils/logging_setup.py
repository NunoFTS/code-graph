from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any


class RunIdFilter(logging.Filter):
    def __init__(self, run_id: str) -> None:
        super().__init__()
        self._run_id = run_id

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        record.run_id = self._run_id
        return True


class JsonFormatter(logging.Formatter):
    _reserved = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
    }

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()

        payload: dict[str, Any] = {
            "ts": ts,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "event": getattr(record, "event", None),
            "run_id": getattr(record, "run_id", None),
            "file": record.pathname,
            "line": record.lineno,
            "func": record.funcName,
        }

        for key, value in record.__dict__.items():
            if key in self._reserved or key in payload:
                continue
            payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(*, logs_dir: Path, testing: bool, run_id: str | None = None) -> str:
    resolved_run_id = run_id or uuid.uuid4().hex

    logs_dir.mkdir(parents=True, exist_ok=True)
    logfile = logs_dir / "app.jsonl"

    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    level = logging.DEBUG if testing else logging.INFO
    root_logger.setLevel(level)

    run_filter = RunIdFilter(resolved_run_id)
    formatter = JsonFormatter()

    file_handler = TimedRotatingFileHandler(
        filename=str(logfile),
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
        delay=True,
    )
    file_handler.setLevel(level)
    file_handler.addFilter(run_filter)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    if testing:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.addFilter(run_filter)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    logging.getLogger(__name__).info("logging_configured", extra={"event": "logging_configured", "logfile": str(logfile)})
    return resolved_run_id
