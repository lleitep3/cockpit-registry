"""Read-only NerdGraph client. No arbitrary GraphQL or mutation transport."""

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, NoReturn

ENDPOINTS = {
    "US": "https://api.newrelic.com/graphql",
    "EU": "https://api.eu.newrelic.com/graphql",
    "JP": "https://api.jp.newrelic.com/graphql",
}
MAX_BYTES = 2_000_000
QUERIES = {
    "synthetics": "FROM SyntheticCheck SELECT count(*), percentage(count(*), WHERE result = 'SUCCESS'), average(duration) FACET monitorName SINCE 30 minutes ago LIMIT 50",
    "apm": "FROM Transaction SELECT rate(count(*), 1 minute), percentile(duration, 95), percentage(count(*), WHERE error IS true) FACET appName SINCE 30 minutes ago LIMIT 50",
    "hosts": "FROM SystemSample SELECT latest(cpuPercent), latest(memoryUsedPercent) FACET hostname SINCE 30 minutes ago LIMIT 50",
    "errors": "FROM TransactionError SELECT count(*) FACET appName, error.class SINCE 30 minutes ago LIMIT 50",
    "incidents": "FROM NrAiIncident SELECT count(*) FACET state, priority SINCE 1 day ago LIMIT 50",
}


class ClientError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> NoReturn:
        raise ClientError("HTTP redirect refused; credentials were not forwarded.")


def credential() -> str:
    """Use one explicit source; refuse publicly readable credential files."""
    value = os.environ.get("NEW_RELIC_API_KEY")
    filename = os.environ.get("NEW_RELIC_API_KEY_FILE")
    if value and filename:
        raise ClientError("Set only NEW_RELIC_API_KEY or NEW_RELIC_API_KEY_FILE.")
    if filename:
        with open(filename, "r", encoding="utf-8") as stream:
            info = os.fstat(stream.fileno())
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_mode & 0o077
                or info.st_uid != os.getuid()
            ):
                raise ClientError(
                    "Credential file must be owned by you and mode 0600/0400."
                )
            value = stream.read(513).strip()
    if (
        not value
        or not value.startswith("NRAK-")
        or len(value) > 512
        or any(c.isspace() for c in value)
    ):
        raise ClientError(
            "Provide a User API key securely through environment or a private file."
        )
    return value


def profiles_path() -> Path:
    return Path.home() / ".cockpit" / "newrelic" / "profiles.json"


def load_profiles() -> dict[str, Any]:
    path = profiles_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            raise ClientError("Invalid profile metadata.")
        return data
    except ValueError:
        raise ClientError(
            "Invalid profile file; restore its metadata before continuing."
        ) from None


def save_profile(name: str, account: int, region: str, vault_key: str) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,62}", name):
        raise ClientError(
            "Profile name must use lowercase letters, digits and hyphens."
        )
    if not re.fullmatch(r"newrelic-[a-z0-9-]{1,100}", vault_key):
        raise ClientError(
            "Vault reference must start with newrelic- and contain no secret."
        )
    data = load_profiles()
    if name in data:
        raise ClientError("Profile exists; choose a new name. Nothing overwritten.")
    data[name] = {"account_id": account, "region": region, "vault_key": vault_key}
    path = profiles_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        json.dump(data, stream)
        temporary = stream.name
    os.replace(temporary, path)


def resolve_profile(args: argparse.Namespace) -> dict[str, Any]:
    name = getattr(args, "profile", None)
    if not name:
        raise ClientError("Select --profile NAME.")
    profile = load_profiles().get(name)
    if not isinstance(profile, dict):
        raise ClientError("Unknown profile.")
    if (
        not isinstance(profile.get("account_id"), int)
        or profile["account_id"] <= 0
        or profile.get("region") not in ENDPOINTS
        or not re.fullmatch(
            r"newrelic-[a-z0-9-]{1,100}", str(profile.get("vault_key", ""))
        )
    ):
        raise ClientError("Invalid profile metadata.")
    if (
        args.account is not None
        or args.region is not None
        or any(
            os.environ.get(x)
            for x in [
                "NEW_RELIC_API_KEY",
                "NEW_RELIC_API_KEY_FILE",
                "NEW_RELIC_ACCOUNT_ID",
                "NEW_RELIC_REGION",
            ]
        )
    ):
        raise ClientError(
            "Profile conflicts with explicit account/region or legacy environment; unset overrides."
        )
    args.account, args.region = profile["account_id"], profile["region"]
    return profile


def vault_credential(reference: str) -> str:
    result = subprocess.run(
        ["cockpit", "vault", "get", reference],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode:
        raise ClientError(
            "Vault unavailable, locked or credential missing; no fallback used."
        )
    value = result.stdout.strip()
    if (
        not value.startswith("NRAK-")
        or len(value) > 512
        or any(c.isspace() for c in value)
    ):
        raise ClientError("Vault entry is not a User API key.")
    return value


def profile_command(args: argparse.Namespace) -> dict[str, Any]:
    if args.profile_action == "list":
        return {"profiles": load_profiles()}
    if args.profile_action == "add":
        save_profile(
            args.name, args.profile_account, args.profile_region, args.vault_key
        )
        return {"profile": args.name, "credential_saved": False}
    profile = resolve_profile(args)
    if not sys.stdin.isatty():
        raise ClientError(
            "Auth requires an interactive terminal with hidden input; never paste a key into chat."
        )
    result = subprocess.run(
        ["cockpit", "vault", "set", profile["vault_key"]], check=False
    )
    if result.returncode:
        raise ClientError("Vault did not save credential.")
    return {"profile": args.profile, "credential_saved": True}


def scrub(value: Any, secret: str) -> Any:
    if isinstance(value, dict):
        return {
            k: "[REDACTED]"
            if re.search(
                r"password|secret|token|api.?key|authorization", k, re.IGNORECASE
            )
            else scrub(v, secret)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [scrub(v, secret) for v in value]
    if isinstance(value, str):
        return re.sub(
            r"NRAK-[A-Za-z0-9_-]+", "[REDACTED]", value.replace(secret, "[REDACTED]")
        )
    return value


def request(
    query: str, variables: dict[str, Any], key: str, region: str
) -> dict[str, Any]:
    req = urllib.request.Request(
        ENDPOINTS[region],
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"API-Key": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.build_opener(NoRedirect()).open(
            req, timeout=45
        ) as response:
            data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ClientError("Response too large; narrow the time window or LIMIT.")
        result = json.loads(data)
    except urllib.error.HTTPError as exc:
        raise ClientError(
            f"New Relic HTTP {exc.code}; check access, region or quota. No automatic retry."
        ) from None
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise ClientError("Network failure or invalid API response.") from None
    if not isinstance(result, dict) or result.get("errors") or "data" not in result:
        raise ClientError(
            "NerdGraph rejected the query or returned partial data; check account, access and NRQL."
        )
    data = result["data"]
    if not isinstance(data, dict):
        raise ClientError("NerdGraph returned no data.")
    return dict(scrub(data, key))


def validate_nrql(query: str) -> str:
    if not re.match(r"^\s*(SELECT|FROM)\b", query, re.IGNORECASE) or re.search(
        r"\b(DELETE|INSERT|DROP|UPDATE)\b|;", query, re.IGNORECASE
    ):
        raise ClientError("Only a single SELECT/FROM read query is supported.")
    if not re.search(r"\bSELECT\b", query, re.IGNORECASE) or not re.search(
        r"\bSINCE\b", query, re.IGNORECASE
    ):
        raise ClientError("Queries must include SELECT and an explicit SINCE window.")
    if len(query) > 16000:
        raise ClientError("Query too long.")
    return query


def positive(value: str) -> int:
    try:
        result = int(value)
        if result > 0:
            return result
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("Account ID must be a positive integer.")


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "configure":
        if args.configure_action == "browser":
            script = Path(__file__).resolve().parents[1] / "bin/setup-browser"
            if subprocess.run([str(script)], check=False).returncode:
                raise ClientError("Browser dependency setup failed.")
            return {"browser_dependency_ready": True}
        import key_setup

        try:
            return key_setup.execute(args)
        except key_setup.ClientError as exc:
            raise ClientError(str(exc)) from None
        except Exception:  # noqa: BLE001 - fail closed without echoing browser/API secrets
            raise ClientError(
                "Key setup stopped. No automatic retry. Check browser login/policy, vault and local journal; raw errors are hidden to protect credentials."
            ) from None
    if args.command == "scaffold":
        target = Path(args.directory)
        if target.exists():
            raise ClientError(
                "Destination exists; choose a new directory. Nothing overwritten."
            )
        shutil.copytree(
            Path(__file__).resolve().parents[1] / "templates" / "availability", target
        )
        return {
            "directory": str(target.resolve()),
            "planned_resources": 9,
            "applied": False,
        }
    if args.command == "profiles":
        return profile_command(args)
    if getattr(args, "profile", None):
        key = vault_credential(resolve_profile(args)["vault_key"])
    else:
        args.account = (
            args.account or positive(os.environ["NEW_RELIC_ACCOUNT_ID"])
            if os.environ.get("NEW_RELIC_ACCOUNT_ID")
            else args.account
        )
        args.region = args.region or os.environ.get("NEW_RELIC_REGION", "US")
        key = credential()
    if args.region not in ENDPOINTS:
        raise ClientError("Unsupported region.")
    if not args.account:
        raise ClientError("Supply --account or NEW_RELIC_ACCOUNT_ID.")
    if args.command == "account":
        data = request(
            "query($id:Int!){actor{account(id:$id){id name}}}",
            {"id": args.account},
            key,
            args.region,
        )
        account = (data.get("actor") or {}).get("account")
        if not account or account.get("id") != args.account:
            raise ClientError("Account inaccessible or mismatched.")
        return {"account": account, "region": args.region}
    nrql = (
        Path(args.file).read_text() if args.command == "nrql" else QUERIES[args.command]
    )
    nrql = validate_nrql(nrql)
    data = request(
        "query($id:Int!,$q:Nrql!){actor{account(id:$id){nrql(query:$q,timeout:30){results}}}}",
        {"id": args.account, "q": nrql},
        key,
        args.region,
    )
    account = (data.get("actor") or {}).get("account")
    if not account or not isinstance(account.get("nrql"), dict):
        raise ClientError("No query result; do not interpret missing data as healthy.")
    return {
        "account_id": args.account,
        "region": args.region,
        "query": nrql,
        "results": account["nrql"]["results"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="cockpit newrelic",
        description="New Relic read-only analysis and Terraform scaffolding. Credentials never accepted as arguments.",
    )
    parser.add_argument("--account", type=positive)
    parser.add_argument("--region", choices=ENDPOINTS)
    parser.add_argument("--profile")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["account", *QUERIES]:
        sub.add_parser(name)
    sub.add_parser("nrql").add_argument("--file", required=True)
    sub.add_parser("scaffold").add_argument("directory")
    profiles = sub.add_parser("profiles").add_subparsers(
        dest="profile_action", required=True
    )
    profiles.add_parser("list")
    profiles.add_parser("auth")
    add = profiles.add_parser("add")
    add.add_argument("name")
    add.add_argument("--account", dest="profile_account", required=True, type=positive)
    add.add_argument(
        "--region", dest="profile_region", required=True, choices=ENDPOINTS
    )
    add.add_argument("--vault-key", required=True)
    configure = sub.add_parser(
        "configure", help="Configuração guiada de navegador e chaves"
    ).add_subparsers(dest="configure_action", required=True)
    configure.add_parser(
        "browser", help="Instalar dependência CDP em ambiente virtual privado"
    )
    keys = configure.add_parser(
        "keys", help="Login no navegador, criação de chaves e armazenamento no cofre"
    )
    keys.add_argument(
        "--profile",
        dest="setup_profile",
        help="Perfil de conta/região; sem opção, pergunta no terminal",
    )
    keys.add_argument(
        "--types", nargs="+", choices=["user", "license", "browser"], default=["user"]
    )
    keys.add_argument(
        "--plan",
        action="store_true",
        help="Prévia JSON sem navegador, cofre ou criação",
    )
    args = parser.parse_args()
    try:
        print(json.dumps(run(args), ensure_ascii=False))
        return 0
    except (
        KeyboardInterrupt,
        EOFError,
        ClientError,
        OSError,
        subprocess.TimeoutExpired,
        UnicodeError,
        argparse.ArgumentTypeError,
    ) as exc:
        # Never echo transport bodies, environment, paths supplied as secrets, or NRQL.
        print(
            str(exc) if isinstance(exc, ClientError) else "Local file access failed.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
