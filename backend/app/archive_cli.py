"""Command-line interface for portable KOMAROVA_CORE database archives."""
from __future__ import annotations

import argparse
import json

from .archive import export_archive, restore_archive, verify_archive
from .database import build_engine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KOMAROVA_CORE archive tools")
    commands = parser.add_subparsers(dest="command", required=True)

    export_command = commands.add_parser("export", help="Create a checksummed database archive")
    export_command.add_argument("archive_path")

    verify_command = commands.add_parser("verify", help="Verify archive checksum and database integrity")
    verify_command.add_argument("archive_path")

    restore_command = commands.add_parser("restore", help="Restore into a new SQLite database file")
    restore_command.add_argument("archive_path")
    restore_command.add_argument("destination")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "export":
        engine = build_engine()
        try:
            path = export_archive(engine, args.archive_path)
        finally:
            engine.dispose()
        print(f"Archive created: {path}")
    elif args.command == "verify":
        manifest = verify_archive(args.archive_path)
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    elif args.command == "restore":
        path = restore_archive(args.archive_path, args.destination)
        print(f"Database restored to new file: {path}")


if __name__ == "__main__":
    main()
