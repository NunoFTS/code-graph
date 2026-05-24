import subprocess
import tempfile
import os

def run_code(code: str, timeout: float = 2.0) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, "main.py")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            result = subprocess.run(
                ["python", file_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "timeout": False,
                "timeout_s": timeout,
            }

        except subprocess.TimeoutExpired as exc:
            return {
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
                "returncode": None,
                "timeout": True,
                "error": "Timeout",
                "timeout_s": timeout,
            }
