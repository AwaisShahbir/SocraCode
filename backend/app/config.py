import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Settings:
    """Application settings with environment variable fallbacks."""

    host: str = os.getenv("SOCRA_HOST", "127.0.0.1")
    port: int = int(os.getenv("SOCRA_PORT", "8000"))
    environment: str = os.getenv("SOCRA_ENV", "development")

    # Allowed CORS origins
    cors_origins: List[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "SOCRA_CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
            ).split(",")
            if origin.strip()
        ]
    )

    # Runner settings
    runner_type: str = os.getenv("RUNNER_TYPE", "local")  # "local" or "docker"
    runner_timeout_seconds: float = float(os.getenv("RUNNER_TIMEOUT_SECONDS", "5.0"))
    runner_max_output_bytes: int = int(os.getenv("RUNNER_MAX_OUTPUT_BYTES", "65536"))

    # Database settings
    db_path: str = os.getenv(
        "SOCRA_DB_PATH",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "socracode.db"),
    )


settings = Settings()
