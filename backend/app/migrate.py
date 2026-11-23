from __future__ import annotations

from .database import build_engine, run_migrations


def main() -> None:
    engine = build_engine()
    try:
        run_migrations(engine)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
