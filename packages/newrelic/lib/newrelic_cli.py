"""Read-only NerdGraph client. No arbitrary GraphQL or mutation transport."""

import argparse
import json
import os
import re
import shutil
import stat
import sys
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
    if not args.account:
        raise ClientError("Supply --account or NEW_RELIC_ACCOUNT_ID.")
    key = credential()
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
        description="New Relic read-only analysis and Terraform scaffolding. Credentials never accepted as arguments."
    )
    parser.add_argument(
        "--account", type=positive, default=os.environ.get("NEW_RELIC_ACCOUNT_ID")
    )
    parser.add_argument(
        "--region", choices=ENDPOINTS, default=os.environ.get("NEW_RELIC_REGION", "US")
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["account", *QUERIES]:
        sub.add_parser(name)
    sub.add_parser("nrql").add_argument("--file", required=True)
    sub.add_parser("scaffold").add_argument("directory")
    args = parser.parse_args()
    try:
        if args.region not in ENDPOINTS:
            raise ClientError("Unsupported region; choose US, EU or JP.")
        print(json.dumps(run(args), ensure_ascii=False))
        return 0
    except (ClientError, OSError) as exc:
        # Never echo transport bodies, environment, paths supplied as secrets, or NRQL.
        print(
            str(exc) if isinstance(exc, ClientError) else "Local file access failed.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
