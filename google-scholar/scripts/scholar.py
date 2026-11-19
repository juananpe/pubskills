"""CLI for the SerpAPI Google Scholar engine. Uses the Python standard library."""

import argparse
import json
import os
from pathlib import Path
import re
import sys
from tempfile import NamedTemporaryFile
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
KEY_NAME = "SERPAPI_API_KEY"
KEY_LINE = re.compile(r"^\s*(?:export\s+)?" + KEY_NAME + r"\s*=\s*(.*)$")
TOKEN = re.compile(r"[A-Za-z0-9_-]+")
ENDPOINT = "https://serpapi.com/search.json"


def env_lines(path):
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []


def file_key(path):
    key = ""
    for line in env_lines(path):
        match = KEY_LINE.fullmatch(line)
        if match:
            key = match[1].partition("#")[0].strip().strip("\"'").strip()
    return key


def get_key():
    return (
        file_key(ENV_FILE)
        or os.environ.get(KEY_NAME, "").strip()
        or file_key(Path.cwd() / ".env")
    )


def save_key(key):
    lines = [line for line in env_lines(ENV_FILE) if not KEY_LINE.fullmatch(line)]
    lines.append(f"{KEY_NAME}={key}")
    temp_path = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix=".env.",
            dir=ENV_FILE.parent, delete=False,
        ) as temporary:
            temp_path = Path(temporary.name)
            temporary.write("\n".join(lines) + "\n")
        os.replace(temp_path, ENV_FILE)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def emit(payload, exit_code=0):
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return exit_code


def fail(code):
    return emit({"status": code}, 1)


def summarize(result):
    publication = result.get("publication_info") or {}
    cited_by = (result.get("inline_links") or {}).get("cited_by") or {}
    return {
        "title": result.get("title"),
        "result_id": result.get("result_id"),
        "link": result.get("link"),
        "snippet": result.get("snippet"),
        "publication": publication.get("summary"),
        "authors": [author["name"] for author in publication.get("authors", [])
                    if author.get("name")],
        "citation_count": cited_by.get("total"),
        "cites_id": cited_by.get("cites_id"),
        "resources": [
            {"format": resource.get("file_format"), "link": resource.get("link")}
            for resource in result.get("resources", []) if resource.get("link")
        ],
    }


def search(args, key):
    params = {"engine": "google_scholar", "api_key": key, "num": args.num,
              "start": args.start}
    for name, value in (
        ("q", args.query), ("cites", args.cites), ("as_ylo", args.year_from),
        ("as_yhi", args.year_to), ("lr", args.language),
    ):
        if value is not None:
            params[name] = value

    try:
        with urlopen(f"{ENDPOINT}?{urlencode(params)}", timeout=30) as response:
            data = json.load(response)
        api_status = (data.get("search_metadata") or {}).get("status")
        if api_status != "Success":
            return fail("serpapi_error")
        results = [summarize(result) for result in data.get("organic_results", [])]
        return emit({"status": "ok", "results": results})
    except HTTPError as error:
        status = {401: "invalid_key", 403: "forbidden", 429: "rate_limit"}
        error.close()
        return fail(status.get(error.code, "serpapi_error"))
    except (URLError, TimeoutError, OSError):
        return fail("network_error")
    except (ValueError, TypeError, AttributeError, KeyError):
        return fail("invalid_response")


def main():
    parser = argparse.ArgumentParser(description="Buscar en Google Scholar con SerpAPI.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="Comprobar si hay una clave configurada.")
    commands.add_parser("set-key", help="Guardar una clave recibida por stdin.")
    query = commands.add_parser("search", help="Buscar artículos y otros documentos.")
    query.add_argument("--query", help="Consulta de Google Scholar.")
    query.add_argument("--cites", help="Identificador del artículo citado.")
    query.add_argument("--year-from", type=int, help="Primer año incluido.")
    query.add_argument("--year-to", type=int, help="Último año incluido.")
    query.add_argument("--language", help="Filtro de idioma de Scholar (p. ej., lang_es).")
    query.add_argument("--num", type=int, default=10, help="Resultados, entre 1 y 20.")
    query.add_argument("--start", type=int, default=0, help="Resultados que se omiten.")
    args = parser.parse_args()

    try:
        if args.command == "set-key":
            key = sys.stdin.readline().strip()
            if not TOKEN.fullmatch(key):
                return fail("invalid_key_format")
            save_key(key)
            return emit({"status": "configured"})

        key = get_key()
    except (OSError, UnicodeError):
        return fail("configuration_error")

    if not key:
        return fail("missing_key")
    if args.command == "status":
        return emit({"status": "configured"})

    args.query = (args.query or "").strip() or None
    if not args.query and not args.cites:
        query.error("indica --query o --cites")
    if args.cites is not None and not re.fullmatch(r"[0-9]+", args.cites):
        query.error("--cites debe ser un identificador numérico")
    if not 1 <= args.num <= 20 or args.start < 0:
        query.error("--num debe estar entre 1 y 20 y --start debe ser mayor o igual a 0")
    if args.year_from is not None and args.year_to is not None:
        if args.year_from > args.year_to:
            query.error("--year-from debe ser menor o igual que --year-to")
    return search(args, key)


if __name__ == "__main__":
    sys.exit(main())
