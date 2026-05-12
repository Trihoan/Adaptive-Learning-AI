import os
from pathlib import Path
from urllib.parse import quote_plus

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parents[3]

if load_dotenv:
    load_dotenv(BASE_DIR / ".env")


def _read_secret_file(filename: str):
    path = BASE_DIR / filename
    if not path.exists():
        return None

    value = path.read_text(encoding="utf-8").strip()
    return value or None


def _build_tidb_uri():
    tidb_password = os.environ.get("TIDB_PASSWORD") or _read_secret_file("passTiDb")
    if not tidb_password:
        return None

    tidb_user = os.environ.get("TIDB_USER", "cDD5zZgTwC6PzXq.root")
    tidb_host = os.environ.get("TIDB_HOST", "gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com")
    tidb_port = os.environ.get("TIDB_PORT", "4000")
    tidb_db = os.environ.get("TIDB_DB", "adaptive_learning_db")

    return (
        "mysql+pymysql://"
        f"{quote_plus(tidb_user)}:{quote_plus(tidb_password)}"
        f"@{tidb_host}:{tidb_port}/{tidb_db}"
        "?ssl_verify_cert=true&ssl_verify_identity=true"
    )


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hoc-tap-ai-bi-mat-2026"
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") # Sẽ được lấy từ file .env

    # Priority: explicit DATABASE_URL, local TiDB settings, then local XAMPP MySQL.
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or _build_tidb_uri()
        or "mysql+pymysql://root:@localhost:3306/adaptive_learning_db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
