# Security

## The signing key

Every Connect IQ build is signed with a developer key (`ciq/keys/developer_key.der`). It is a
**private key**:

- It is never committed. `ciq/keys/` is gitignored, and three independent gates block it:
  the pre-commit `gitleaks` and `detect-private-key` hooks, and a CI job that scans the full
  history and fails if any key file or build output is tracked.
- Keep a backup somewhere safe (a password manager or an encrypted drive). Once a version is in
  the Connect IQ Store, **every update must be signed with the same key**. A lost key means the
  store app can never be updated, only replaced by a new listing.
- If you fork this project, generate your own key (see [docs/USER_MANUAL.md](docs/USER_MANUAL.md)).
  Never reuse someone else's.

## What else stays local

- Build output: `*.prg`, `*.iq`, `ciq/gen/`, the compiler's `*-mir/` intermediates, `release/`.
- Machine-specific paths are written as `%APPDATA%` / `$APPDATA`, never as a user's home path.

## Reporting a problem

If you find a secret or personal data in this repository, please open an issue saying *where*
without quoting the value, or contact the maintainer through GitHub.

## Permissions the watch face asks for

Only **UserProfile**. It is used to read your own heart-rate zone thresholds so the gauge
matches your zones. Nothing is sent anywhere: the face has no network, storage or background
code.
