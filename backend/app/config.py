import os
from pathlib import Path
from dotenv import load_dotenv


def load_project_env() -> None:
    """Load environment variables from a project .env file.

    Priority:
    1. root/.env
    2. backend/.env
    """
    base_dir = Path(__file__).resolve().parents[2]
    env_candidates = [base_dir / ".env", base_dir / "backend" / ".env"]
    for env_path in env_candidates:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            return
