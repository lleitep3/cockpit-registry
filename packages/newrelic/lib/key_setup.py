"""Interactive Linux Chrome/CDP bootstrap. Never emit secrets or browser snapshots."""

import argparse
import fcntl
import hmac
import json
import os
import pty
import re
import select
import shutil
import subprocess
import sys
import tempfile
import termios
import time
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import newrelic_cli as nr
from newrelic_cli import ClientError

__all__ = ["ClientError", "execute"]

LOGIN_TIMEOUT = 600
BROWSER_TIMEOUT = 30
VAULT_TIMEOUT = 30
HOSTS = {
    "US": "one.newrelic.com",
    "EU": "one.eu.newrelic.com",
    "JP": "one.jp.newrelic.com",
}


def atomic_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        json.dump(data, stream)
        temporary = stream.name
    os.replace(temporary, path)


def vault_ready() -> None:
    result = subprocess.run(
        ["cockpit", "vault", "status"],
        capture_output=True,
        text=True,
        timeout=VAULT_TIMEOUT,
        check=False,
    )
    if result.returncode or not (
        "Status: 🔓 UNLOCKED" in result.stdout
        or "✓ cockpit-cli: 🔓 Unlocked" in result.stdout
    ):
        raise nr.ClientError(
            "Unlock the Cockpit vault yourself before creating keys. No lock bypass is attempted."
        )


def vault_save(reference: str, secret: str) -> None:
    """Send only after the real vault prompt has disabled terminal echo."""
    master, slave = pty.openpty()
    process = subprocess.Popen(
        ["cockpit", "vault", "set", "--namespace", "newrelic", reference],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        close_fds=True,
    )
    try:
        deadline = time.monotonic() + VAULT_TIMEOUT
        prompt = b""
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise nr.ClientError(
                    "Vault exited before secure input; credential not saved."
                )
            if select.select([master], [], [], 0.1)[0]:
                prompt += os.read(master, 4096)
            if (
                b"Enter secret for" in prompt
                and not termios.tcgetattr(slave)[3] & termios.ECHO
            ):
                os.write(master, secret.encode() + b"\n")
                break
        else:
            raise nr.ClientError("Vault secure-input timeout; credential not saved.")
        if process.wait(timeout=VAULT_TIMEOUT):
            raise nr.ClientError(
                "Vault save failed; inspect the newly created key manually before retrying."
            )
        result = subprocess.run(
            ["cockpit", "vault", "get", "--namespace", "newrelic", reference],
            capture_output=True,
            text=True,
            timeout=VAULT_TIMEOUT,
            check=False,
        )
        if result.returncode or not hmac.compare_digest(result.stdout.strip(), secret):
            raise nr.ClientError("Vault read-back verification failed.")
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        os.close(master)
        os.close(slave)


def check_account(key: str, account: int, region: str) -> None:
    data = nr.request(
        "query($id:Int!){actor{account(id:$id){id}}}", {"id": account}, key, region
    )
    if ((data.get("actor") or {}).get("account") or {}).get("id") != account:
        raise nr.ClientError("Key does not grant access to the selected account.")


def browser_url(region: str, account: int) -> str:
    return f"https://{HOSTS[region]}/admin-portal/api-keys/home?account={account}"


def require_origin(url: str, region: str) -> None:
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != HOSTS[region]
        or parsed.port not in (None, 443)
    ):
        raise nr.ClientError(
            "Unexpected origin; complete login yourself. No page action performed."
        )


def user_key_from_page(
    page: Any, account: int, region: str, name: str, journal: Path
) -> str:
    """Only stable visible controls; fail closed if UI changes."""
    require_origin(page.url, region)
    page.get_by_role("button", name="Create a key", exact=True).wait_for(
        timeout=LOGIN_TIMEOUT * 1000
    )
    if name in page.locator("body").inner_text():
        raise nr.ClientError(
            "Key name already exists; recover it manually instead of creating a duplicate."
        )
    page.get_by_role("button", name="Create a key", exact=True).click()
    field = page.get_by_role("textbox", name="Name", exact=True)
    field.wait_for(timeout=15000)
    account_text = page.get_by_role("button", name="Account", exact=True).inner_text()
    ids = re.findall(r"Account:\s*(\d+)\s*-", account_text)
    if ids != [str(account)]:
        raise nr.ClientError("Account selector does not match requested account.")
    if (
        page.get_by_role("button", name="Key type", exact=True).inner_text().strip()
        != "User"
    ):
        raise nr.ClientError(
            "Expected User key type; refusing another credential type."
        )
    field.fill(name)
    page.get_by_role("textbox", name="Notes", exact=True).fill(
        "Managed by Cockpit; User key for Terraform and read queries."
    )
    buttons = page.get_by_role("button", name="Create a key", exact=True)
    if buttons.count() != 2:
        raise nr.ClientError("Unexpected create dialog; nothing submitted.")
    require_origin(page.url, region)
    atomic_json(
        journal,
        {
            "status": "submission-started",
            "name": name,
            "type": "USER",
            "account_id": account,
        },
    )
    buttons.last.click()
    page.get_by_role("button", name="Copy Key", exact=True).wait_for(timeout=15000)
    require_origin(page.url, region)
    keys = set(
        re.findall(r"NRAK-[A-Za-z0-9_-]{20,}", page.locator("body").inner_text())
    )
    if len(keys) != 1:
        raise nr.ClientError(
            "Unable to capture exactly one new key; reconcile journal manually. No retry."
        )
    return str(keys.pop())


def launch_user_bootstrap(
    account: int, region: str, name: str, journal: Path, profile: str
) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise nr.ClientError(
            "Dependência de navegador ausente. Rode cockpit newrelic configure browser e tente novamente."
        ) from None
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome:
        raise nr.ClientError("Install Chrome/Chromium from its official source first.")
    directory = nr.profiles_path().parent / "browser" / profile
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    active = directory / "DevToolsActivePort"
    started = time.time()
    process = subprocess.Popen(
        [
            chrome,
            f"--user-data-dir={directory}",
            "--remote-debugging-address=127.0.0.1",
            "--remote-debugging-port=0",
            "--no-first-run",
            "--no-default-browser-check",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + BROWSER_TIMEOUT
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise nr.ClientError(
                    "Chrome did not start; close the dedicated Cockpit browser before retrying."
                )
            if active.exists() and active.stat().st_mtime >= started:
                break
            time.sleep(0.1)
        else:
            raise nr.ClientError(
                "CDP unavailable. Check Chrome policy; do not bypass administrative restrictions."
            )
        port = int(active.read_text().splitlines()[0])
        if not 1 <= port <= 65535:
            raise nr.ClientError("Invalid local CDP port.")
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            page = browser.contexts[0].new_page()
            page.goto(browser_url(region, account))
            print(
                "Faça login/MFA no navegador do Cockpit. Complete senhas e CAPTCHA pessoalmente; o comando aguardará até 10 minutos.",
                file=sys.stderr,
            )
            page.get_by_role("button", name="Create a key", exact=True).wait_for(
                timeout=LOGIN_TIMEOUT * 1000
            )
            return user_key_from_page(page, account, region, name, journal)
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def create_ingest(
    key: str, account: int, region: str, kind: str, name: str
) -> dict[str, str]:
    if kind not in ("LICENSE", "BROWSER"):
        raise nr.ClientError("Unsupported ingest key type.")
    query = (
        "mutation($id:Int!,$name:String!){apiAccessCreateKeys(keys:{ingest:{accountId:$id,ingestType:"
        + kind
        + ",name:$name}}){createdKeys{id key name type ... on ApiAccessIngestKey{ingestType}} errors{type}}}"
    )
    request = urllib.request.Request(
        nr.ENDPOINTS[region],
        data=json.dumps(
            {"query": query, "variables": {"id": account, "name": name}}
        ).encode(),
        headers={"API-Key": key, "Content-Type": "application/json"},
    )
    with urllib.request.build_opener(nr.NoRedirect()).open(
        request, timeout=45
    ) as response:
        raw = response.read(nr.MAX_BYTES + 1)
    if len(raw) > nr.MAX_BYTES:
        raise nr.ClientError("Oversized key response; reconcile manually. No retry.")
    data = json.loads(raw)
    result = (data.get("data") or {}).get("apiAccessCreateKeys") or {}
    keys = result.get("createdKeys") or []
    if data.get("errors") or result.get("errors") or len(keys) != 1:
        raise nr.ClientError(
            "Key API returned failure/partial success. Reconcile manually; no retry."
        )
    created = keys[0]
    if (
        created.get("type") != "INGEST"
        or created.get("ingestType") != kind
        or not created.get("key")
    ):
        raise nr.ClientError("Unexpected key response; no retry.")
    return {"id": str(created["id"]), "key": str(created["key"])}


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if any(os.environ.get(k) for k in ("DEBUG", "PWDEBUG")):
        raise nr.ClientError("Unset DEBUG/PWDEBUG to prevent credential traces.")
    args.types = list(dict.fromkeys(args.types))
    profile_name = args.setup_profile or args.profile
    if not profile_name and sys.stdin.isatty():
        names = list(nr.load_profiles())
        print("Perfis disponíveis: " + (", ".join(names) or "nenhum"), file=sys.stderr)
        default = names[0] if len(names) == 1 else ""
        profile_name = (
            input(f"Perfil New Relic (novo ou existente) [{default}]: ").strip()
            or default
        )
    if not profile_name or not re.fullmatch(r"[a-z][a-z0-9-]{0,62}", profile_name):
        raise nr.ClientError("Select an existing --profile NAME.")
    if profile_name not in nr.load_profiles():
        if args.plan or not sys.stdin.isatty():
            raise nr.ClientError(
                "Profile missing; use profiles add NAME --account ID --region US --vault-key newrelic-NAME."
            )
        account = nr.positive(input("ID da conta New Relic: ").strip())
        region = input("Região de dados [US/EU/JP]: ").strip().upper()
        if region not in HOSTS:
            raise nr.ClientError("Região inválida.")
        nr.save_profile(profile_name, account, region, f"newrelic-{profile_name}")
    selection = argparse.Namespace(profile=profile_name, account=None, region=None)
    profile = nr.resolve_profile(selection)
    account, region = selection.account, selection.region
    if args.plan:
        return {
            "profile": profile_name,
            "account_id": account,
            "region": region,
            "types": args.types,
            "browser_profile": "dedicated-persistent",
            "creates_keys": False,
            "requires_login": True,
            "requires_vault_unlock": True,
        }
    if not sys.stdin.isatty():
        raise nr.ClientError(
            "Use --plan for machine-readable preview. Run creation in an interactive terminal for login and confirmation."
        )
    root = nr.profiles_path().parent
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    with open(root / f"{profile_name}.setup.lock", "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise nr.ClientError(
                "Another key setup is running for this profile."
            ) from None
        vault_ready()
        confirmation = f"CREATE {account} {profile_name}"
        print(
            f"Account {account} ({region}), profile {profile_name}. Types: {', '.join(args.types)}. User key inherits your roles; local vault entries may be replaced. No existing remote key is revoked.",
            file=sys.stderr,
        )
        if input(f"Digite {confirmation} para autorizar: ").strip() != confirmation:
            raise nr.ClientError("Cancelled; no key created.")
        return provision(profile_name, profile, args.types, root)


def provision(
    profile_name: str, profile: dict[str, Any], types: list[str], root: Path
) -> dict[str, Any]:
    account, region = profile["account_id"], profile["region"]
    journal = root / f"{profile_name}.key-setup.json"
    state = json.loads(journal.read_text()) if journal.exists() else {}
    if state and state.get("status") != "complete":
        raise nr.ClientError(
            "Previous key creation is unresolved. Review the local journal and New Relic keys before retrying."
        )
    try:
        key = nr.vault_credential(profile["vault_key"])
    except nr.ClientError:
        if "user" not in types:
            raise nr.ClientError(
                "A valid User key is required; include user in --types to bootstrap."
            ) from None
        name = f"cockpit-{profile_name}-user"
        key = launch_user_bootstrap(account, region, name, journal, profile_name)
        check_account(key, account, region)
        vault_save(profile["vault_key"], key)
        atomic_json(
            journal,
            {"status": "complete", "name": name, "type": "USER", "account_id": account},
        )
    # A transport/access failure must never trigger credential creation.
    check_account(key, account, region)
    saved = ["user"]
    for kind in types:
        if kind == "user":
            continue
        field = f"{kind}_vault_key"
        reference = profile.get(field)
        if reference:
            # Existing managed keys are not silently rotated; no raw value is read here.
            stored = subprocess.run(
                ["cockpit", "vault", "get", "--namespace", "newrelic", reference],
                capture_output=True,
                text=True,
                timeout=VAULT_TIMEOUT,
                check=False,
            )
            if stored.returncode or not stored.stdout.strip():
                raise nr.ClientError(
                    "Ingest reference exists but vault entry is unavailable; recover it rather than create another key."
                )
            saved.append(kind)
            continue
        name = f"cockpit-{profile_name}-{kind}"
        atomic_json(
            journal,
            {
                "status": "submission-started",
                "name": name,
                "type": kind,
                "account_id": account,
            },
        )
        created = create_ingest(key, account, region, kind.upper(), name)
        reference = f"newrelic-{profile_name}-{kind}"
        vault_save(reference, created["key"])
        profiles = nr.load_profiles()
        profiles[profile_name][field] = reference
        profiles[profile_name][f"{kind}_key_id"] = created["id"]
        atomic_json(nr.profiles_path(), profiles)
        atomic_json(
            journal,
            {
                "status": "complete",
                "name": name,
                "type": kind,
                "account_id": account,
                "key_id": created["id"],
            },
        )
        saved.append(kind)
    return {
        "profile": profile_name,
        "account_id": account,
        "region": region,
        "configured_types": saved,
        "secret_values_displayed": False,
    }
