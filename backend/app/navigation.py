"""Role-aware navigation manifest for the private KOMAROVA_CORE application.

This manifest exposes only capabilities backed by implemented API routes.
It is data for the private UI, not a claim that a browser UI already exists.
"""

from __future__ import annotations


def build_navigation(role: str) -> dict:
    """Return the navigation entries available to an authenticated role."""
    sections = [
        {
            "key": "registry",
            "title": "Семейный реестр",
            "items": [
                {
                    "key": "people",
                    "title": "Люди",
                    "kind": "registry",
                    "api_endpoint": "/api/v1/people",
                    "permission": "read",
                },
                {
                    "key": "search",
                    "title": "Поиск",
                    "kind": "search",
                    "api_endpoint": "/api/v1/search",
                    "permission": "read",
                },
                {
                    "key": "relationships",
                    "title": "Родственные связи",
                    "kind": "relationships",
                    "api_endpoint": "/api/v1/people/{person_id}/relationships",
                    "permission": "read",
                },
                {
                    "key": "archive",
                    "title": "Семейный архив",
                    "kind": "archive",
                    "api_endpoint": "/api/v1/archive/items",
                    "permission": "read",
                },
            ],
        },
        {
            "key": "account",
            "title": "Моя учётная запись",
            "items": [
                {
                    "key": "profile",
                    "title": "Профиль",
                    "kind": "account",
                    "api_endpoint": "/api/v1/auth/me",
                    "permission": "self",
                },
                {
                    "key": "sessions",
                    "title": "Сеансы входа",
                    "kind": "sessions",
                    "api_endpoint": "/api/v1/auth/sessions",
                    "permission": "self",
                },
            ],
        },
    ]

    if role in {"owner", "moderator", "family_member"}:
        sections.append({
            "key": "archive_intake",
            "title": "Приём материалов",
            "items": [
                {
                    "key": "archive_upload",
                    "title": "Загрузка материалов",
                    "kind": "archive_upload",
                    "api_endpoint": "/api/v1/archive/items",
                    "permission": "write",
                },
            ],
        })

    if role in {"owner", "moderator"}:
        sections.append({
            "key": "administration",
            "title": "Управление",
            "items": [
                {
                    "key": "users",
                    "title": "Учётные записи",
                    "kind": "users",
                    "api_endpoint": "/api/v1/users",
                    "permission": "manage_accounts",
                },
            ],
        })

    return {
        "schema_version": 1,
        "role": role,
        "sections": sections,
    }
