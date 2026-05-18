"""
One-time setup: register newsweek.com with AgentMail, add the required DNS
records, verify the domain, and create the reporting@newsweek.com inbox.

Usage:
    python setup_domain.py

After it completes, copy the printed AGENTMAIL_INBOX_ID into your .env.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from agentmail import AgentMail
from agentmail.inboxes import CreateInboxRequest

DOMAIN       = "newsweek.com"
USERNAME     = "reporting"
DISPLAY_NAME = "Newsweek Reporting"


def _load_dotenv() -> None:
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _print_records(domain) -> None:
    print("\nAdd these DNS records to newsweek.com before continuing:\n")
    print(f"  {'TYPE':<6}  {'NAME':<45}  {'PRI':<4}  VALUE")
    print(f"  {'-'*6}  {'-'*45}  {'-'*4}  {'-'*60}")
    for r in domain.records:
        pri = str(r.priority) if r.priority is not None else ""
        print(f"  {r.type:<6}  {r.name:<45}  {pri:<4}  {r.value}")
    print()


def main() -> None:
    _load_dotenv()
    client = AgentMail(api_key=os.environ["AGENTMAIL_API_KEY"])

    # ── 1. register domain (idempotent: reuse if already registered) ──────────
    existing = {d.domain: d for d in client.domains.list().items}

    if DOMAIN in existing:
        domain = existing[DOMAIN]
        print(f"Domain {DOMAIN!r} already registered (id={domain.domain_id}, status={domain.status}).")
    else:
        domain = client.domains.create(domain=DOMAIN, feedback_enabled=False)
        print(f"Domain {DOMAIN!r} registered (id={domain.domain_id}).")

    # ── 2. show DNS records if not yet verified ────────────────────────────────
    if domain.status != "verified":
        _print_records(domain)
        input("Press Enter once all DNS records are in place...")

        # Poll verify up to ~5 min (DNS can be slow)
        print("Verifying...", end="", flush=True)
        for attempt in range(30):
            try:
                client.domains.verify(domain.domain_id)
                domain = client.domains.get(domain.domain_id)
                if domain.status == "verified":
                    break
            except Exception:
                pass
            print(".", end="", flush=True)
            time.sleep(10)

        print()
        if domain.status != "verified":
            # Re-fetch and show current record statuses
            domain = client.domains.get(domain.domain_id)
            print("\nDomain not verified yet. Current record statuses:")
            for r in domain.records:
                print(f"  [{r.status}]  {r.type}  {r.name}")
            print("\nCheck your DNS provider, then re-run this script.")
            sys.exit(1)

        print(f"Domain {DOMAIN!r} verified.\n")
    else:
        print(f"Domain already verified.\n")

    # ── 3. create inbox (idempotent: reuse if address already exists) ─────────
    address = f"{USERNAME}@{DOMAIN}"
    existing_inboxes = {i.address: i for i in client.inboxes.list().items}

    if address in existing_inboxes:
        inbox = existing_inboxes[address]
        print(f"Inbox {address!r} already exists (id={inbox.inbox_id}).")
    else:
        inbox = client.inboxes.create(
            request=CreateInboxRequest(
                username=USERNAME,
                domain=DOMAIN,
                display_name=DISPLAY_NAME,
            )
        )
        print(f"Inbox created: {address!r} (display_name={DISPLAY_NAME!r}).")

    # ── 4. print next step ────────────────────────────────────────────────────
    print(f"\nDone. Add this to your .env (replacing the old value):\n")
    print(f"  AGENTMAIL_INBOX_ID={inbox.inbox_id}\n")
    print("Emails sent by weekly_report.py will now appear to come from:")
    print(f"  {DISPLAY_NAME} <{address}>")


if __name__ == "__main__":
    main()
