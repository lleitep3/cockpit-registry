#!/usr/bin/env python3
"""Vercel adapter. Profiles and secrets belong to Cockpit core."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

API_ORIGIN = "https://api.vercel.com"
DOCS_URL = "https://vercel.com/docs"
NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
SECRET_KEY = re.compile(
    r"token|secret|password|authorization|cookie|credential|^(value|key)$", re.I
)
BLOCKED_FLAGS = {
    "--token",
    "-t",
    "--scope",
    "-S",
    "--team",
    "-T",
    "--api",
    "-A",
    "--debug",
    "-d",
    "--global-config",
}
BLOCKED_COMMANDS = {"tokens", "login", "logout", "switch"}


class Error(Exception):
    """An actionable failure that contains no raw credentials."""


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # argparse's unknown-argument message can contain an accidentally pasted token.
        raise Error(
            "Invalid arguments. Use --help; --token takes no value; use hidden input or --token-stdin."
        )


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> None:
        raise Error(
            "API redirect refused; credentials are restricted to api.vercel.com."
        )


def identifier(value: str) -> str:
    if not NAME.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "Use a lowercase alias or team slug with hyphens."
        )
    return value


def config_args(profile: str | None = None) -> list[str]:
    command = ["cockpit", "config", "--namespace", "vercel"]
    if profile:
        command += ["--profile", profile]
    return command


def config(profile: str | None, args: list[str], secret: str | None = None) -> str:
    result = subprocess.run(
        config_args(profile) + args,
        input=secret,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        # Vault/backend failures may echo input. Keep the adapter's error generic.
        raise Error(
            "Cockpit config failed. Check profile support and unlock the vercel vault; no plaintext fallback."
        )
    return result.stdout


def store_token(profile: str, token: str) -> None:
    if not token or any(char.isspace() for char in token):
        raise Error("Token is empty or contains whitespace.")
    config(profile, ["secret", "token", "--stdin"], token)


def auth(args: argparse.Namespace) -> int:
    config(None, ["list"])  # Old cores must fail before attempting credential storage.
    try:
        existing = json.loads(config(args.account, ["show"]))
    except Error:
        existing = {}
    scope = args.scope or existing.get("scope", {}).get("value") or args.account
    if not NAME.fullmatch(scope):
        raise Error("Invalid stored scope; pass --scope TEAM_SLUG.")
    if args.token_stdin:
        if sys.stdin.isatty():
            raise Error(
                "--token-stdin requires redirected input; omit it for hidden entry."
            )
        token = sys.stdin.read().strip()
        store_token(args.account, token)
    else:
        if not sys.stdin.isatty():
            raise Error(
                "Hidden entry requires a terminal; use --token-stdin in automation."
            )
        result = subprocess.run(
            config_args(args.account) + ["secret", "token"],
            check=False,
        )
        if result.returncode:
            raise Error("Token was not stored; unlock the vercel vault and retry.")
    config(args.account, ["set", "scope", scope])
    print(json.dumps({"profile": args.account, "stored": True, "verified": False}))
    return 0


def api_url(endpoint: str, scope: str | None) -> str:
    parsed = urlsplit(endpoint)
    if (
        not endpoint.startswith("/")
        or endpoint.startswith("//")
        or parsed.scheme
        or parsed.netloc
        or parsed.fragment
        or "\\" in endpoint
        or any(c.isspace() for c in endpoint)
    ):
        raise Error("API path must be relative, such as /v9/projects.")
    query = parse_qsl(parsed.query, keep_blank_values=True)
    if any(k.lower() in {"slug", "teamid", "token", "access_token"} for k, _ in query):
        raise Error("Account and credentials come only from the selected profile.")
    if scope:
        query.append(("slug", scope))
    return API_ORIGIN + parsed.path + ("?" + urlencode(query) if query else "")


def request(method: str, endpoint: str, scope: str | None, body: Any = None) -> Any:
    token = os.environ.get("VERCEL_TOKEN")
    if not token:
        raise Error("Token unavailable. Authenticate the profile and unlock the vault.")
    payload = None if body is None else json.dumps(body).encode()
    req = Request(
        api_url(endpoint, scope),
        data=payload,
        method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        },
    )
    try:
        with build_opener(NoRedirect()).open(req, timeout=30) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}
    except HTTPError as error:
        hint = {
            401: "Token invalid or expired.",
            403: "Token lacks permission or scope.",
            429: "Rate limited; inspect Retry-After before retrying.",
        }.get(error.code, "Inspect operation state before retrying a write.")
        raise Error(f"Vercel HTTP {error.code}. {hint}") from None
    except (URLError, TimeoutError, OSError, ValueError):
        raise Error(
            "Vercel response unavailable/invalid. Write outcome may be unknown; do not retry blindly."
        ) from None


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if SECRET_KEY.search(key) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        token = os.environ.get("VERCEL_TOKEN", "")
        return value.replace(token, "[REDACTED]") if token else value
    return value


def cli_args(arguments: list[str], scope: str) -> list[str]:
    args = arguments[1:] if arguments[:1] == ["--"] else arguments
    if not args or args[0].startswith("-") or args[0] in BLOCKED_COMMANDS:
        raise Error("Specify a CLI command; use auth/token-create for credentials.")
    for arg in args:
        if arg.split("=", 1)[0] in BLOCKED_FLAGS or any(
            arg.startswith(flag) and arg != flag for flag in ("-t", "-S", "-T", "-A")
        ):
            raise Error("CLI account, token, API and debug overrides are disabled.")
    binary = os.environ.get("VERCEL_CLI") or shutil.which("vercel")
    if not binary or not Path(binary).is_file():
        raise Error(
            "Vercel CLI missing. Install a pinned local version or set VERCEL_CLI."
        )
    return [binary, *args, "--scope", scope, "--non-interactive"]


def run_cli(arguments: list[str], scope: str) -> int:
    command = cli_args(arguments, scope)
    environment = dict(os.environ)
    for key in ("VERCEL_ORG_ID", "VERCEL_PROJECT_ID"):
        environment.pop(key, None)
    environment["VERCEL_TELEMETRY_DISABLED"] = "1"
    result = subprocess.run(
        command, env=environment, capture_output=True, text=True, check=False
    )
    print(redact(result.stdout), end="")
    print(redact(result.stderr), end="", file=sys.stderr)
    return result.returncode


def create_token(args: argparse.Namespace, scope: str) -> int:
    body = {"name": args.name}
    if args.project:
        body["projectId"] = args.project
    result = request("POST", "/v3/user/tokens", None, body)
    secret = result.get("bearerToken")
    metadata = result.get("token", {})
    if not secret:
        raise Error(
            "Token creation response lacks bearerToken; inspect Account Tokens before retrying."
        )
    try:
        store_token(args.save_as, secret)
        config(args.save_as, ["set", "scope", scope])
    except Error:
        raise Error(
            "Token created but vault save failed. Reconcile Account Tokens before retrying; plaintext not retained."
        ) from None
    print(
        json.dumps(
            {
                "profile": args.save_as,
                "stored": True,
                "id": metadata.get("id"),
                "name": args.name,
            }
        )
    )
    return 0


def worker(args: argparse.Namespace) -> int:
    scope = os.environ.get("VERCEL_SCOPE", "")
    if not NAME.fullmatch(scope):
        raise Error(
            "Profile scope is missing/invalid. Run auth with --scope TEAM_SLUG."
        )
    if args.command == "cli":
        return run_cli(args.arguments, scope)
    if args.command == "token-create":
        return create_token(args, scope)
    method, body = "GET", None
    if args.command == "status":
        endpoint = "/v2/teams/" + scope
    elif args.command == "projects":
        endpoint = "/v9/projects?limit=" + str(args.limit)
    elif args.command == "deployments":
        endpoint = "/v6/deployments?limit=" + str(args.limit)
    elif args.command == "inspect":
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", args.deployment):
            raise Error("Use a deployment ID or hostname, not a URL.")
        endpoint = "/v13/deployments/" + args.deployment
    else:
        method, endpoint = args.method, args.path
        if re.search(r"/(?:tokens|env)(?:/|$|\?)", endpoint):
            raise Error(
                "Credential endpoints require dedicated commands or the dashboard."
            )
        if method != "GET" and not args.apply:
            raise Error("Write requires --apply after reviewing the request.")
        if args.body_file:
            body = json.loads(Path(args.body_file).read_text())
    print(json.dumps(redact(request(method, endpoint, scope, body)), indent=2))
    return 0


def build_parser() -> Parser:
    parser = Parser(
        prog="cockpit vercel",
        description="Vercel accounts, API and CLI through Cockpit vault.",
    )
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)
    login = sub.add_parser("auth", help="Store token in vault using hidden input.")
    login.add_argument("account", type=identifier)
    login.add_argument(
        "--scope", type=identifier, help="Vercel team slug; defaults to account alias."
    )
    mode = login.add_mutually_exclusive_group()
    mode.add_argument(
        "--token", action="store_true", help="Hidden token prompt (no value in argv)."
    )
    mode.add_argument("--token-stdin", action="store_true")
    accounts = sub.add_parser("accounts", help="List public account metadata.")
    accounts.add_argument("--profile", type=identifier)
    sub.add_parser("doctor", help="Check local dependencies; no API calls.")
    sub.add_parser("docs", help="Official reference pages.")
    for name in (
        "status",
        "projects",
        "deployments",
        "inspect",
        "api",
        "cli",
        "token-create",
    ):
        command = sub.add_parser(name)
        command.add_argument("--profile", required=True, type=identifier)
        if name in {"projects", "deployments"}:
            command.add_argument(
                "--limit", type=int, choices=range(1, 101), default=20, metavar="1..100"
            )
        elif name == "inspect":
            command.add_argument("deployment")
        elif name == "api":
            command.add_argument(
                "method", choices=["GET", "POST", "PATCH", "PUT", "DELETE"]
            )
            command.add_argument("path")
            command.add_argument("--body-file")
            command.add_argument("--apply", action="store_true")
        elif name == "cli":
            command.add_argument("arguments", nargs=argparse.REMAINDER)
        elif name == "token-create":
            command.add_argument("--name", required=True)
            command.add_argument("--save-as", type=identifier, required=True)
            command.add_argument("--project", help="Optional Vercel project ID.")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        arguments = sys.argv[1:] if argv is None else argv
        args = build_parser().parse_args(arguments)
        if args.command == "auth":
            return auth(args)
        if args.command == "accounts":
            print(config(args.profile, ["show"] if args.profile else ["list"]), end="")
            return 0
        if args.command == "docs":
            print(DOCS_URL + "\n" + DOCS_URL + "/cli\n" + DOCS_URL + "/rest-api")
            return 0
        if args.command == "doctor":
            print(
                json.dumps(
                    {
                        "python": sys.version.split()[0],
                        "cockpit": shutil.which("cockpit"),
                        "vercel_cli": os.environ.get("VERCEL_CLI")
                        or shutil.which("vercel"),
                    }
                )
            )
            config(None, ["list"])
            return 0
        if args.worker:
            return worker(args)
        bindings = []
        if args.command == "cli":
            metadata = json.loads(config(args.profile, ["show"]))
            if metadata.get("cli_path", {}).get("value"):
                bindings = ["--env", "VERCEL_CLI=cli_path"]
        command = config_args(args.profile) + [
            "exec",
            "--env",
            "VERCEL_TOKEN=token",
            "--env",
            "VERCEL_SCOPE=scope",
            *bindings,
            "--",
            sys.executable,
            str(Path(__file__).resolve()),
            "--worker",
            *arguments,
        ]
        return subprocess.run(command, check=False).returncode
    except (Error, OSError, ValueError) as error:
        print("vercel: " + str(redact(str(error))), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
