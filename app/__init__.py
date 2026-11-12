"""Load local settings for Assembly Proof’s Python entry points."""

from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False, interpolate=False)
