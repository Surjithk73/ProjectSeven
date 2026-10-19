# CinemaFlow two-machine setup

Implementation branch: `feature/cinemaflow-multi-provider`. `surjk73` has accepted collaborator write access. The initial client PR awaits human review/merge before the LAN deployment rehearsal. Existing banking examples remain available.

## Machines and repositories

- A: APIShield at `http://127.0.0.1:8002`; Gemini service-account connection stays on A.
- B: CinemaFlow at port 8100, Grand Cinema at 8101, CinemaPay at 8102. Both providers are independent HTTP processes with persistent SQLite state. CinemaPay is a simulation, not an official Google Pay integration.
- ProjectSeven contains APIShield/providers/tooling. APIGuardTesting contains the client under `movie_booking/`, preserving the existing shipping fixture and Git history.

Use Python 3.11+, Git, GitHub CLI, and Node/npm for the APIShield frontend. On a fresh ProjectSeven checkout:

```powershell
py -3.11 -m venv venv
./venv/Scripts/python.exe -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
./demo/scripts/check_environment.ps1
```

## Initial client baseline

The baseline is already published as [client setup PR #2](https://github.com/Surjithk73/APIGuardTesting/pull/2), ready for `surjk73` to review. Use that existing PR; the export command below is only needed when preparing a new clean baseline checkout. This normal setup PR is separate from later AI-generated migrations. Do not merge it automatically. On a clean APIGuardTesting checkout, the export command creates only the movie client, its requirements and its CI workflow; it refuses to overwrite an existing movie client:

```powershell
./venv/Scripts/python.exe -m demo.setup export-client --repository C:/APIShieldDemo/client-source
```

Create a setup branch, commit those additions, run `python -m pytest movie_booking/tests -q` from the client checkout, and publish its PR. Once reviewed and merged, clone/pull `main` separately on A and B. APIShield's repair source must match the GitHub publication base exactly. Do not develop directly inside a deployed release directory.

## Quick single-computer development preview

```powershell
./demo/scripts/start_system_b.ps1
```

Open `http://127.0.0.1:8100`. Book a seat on V1, then use the API providers tab to switch payment or theatre to V2. Booking failures are expected until the corresponding adapter is updated. This preview serves the V1 source template directly; it is not the GitHub deployment rehearsal.

Stop using `./demo/scripts/stop_system_b.ps1`. The runtime owns only its child processes; Windows job objects include deployment descendants. Logs are in the private state directory, not in Git.

## System B: reviewed-merge deployment

Copy `demo/deployment/system-b.example.json` to a private local path such as `C:/APIShieldDemo/system-b.json`. Set `releases` to an empty dedicated folder and confirm `deployment_actor` matches B's GitHub CLI login. Sign in locally using the instructions in `github-accounts.md`. No credential belongs in that JSON.

```powershell
./demo/scripts/start_system_b.ps1 -DeploymentConfig C:/APIShieldDemo/system-b.json
```

The helper explicitly bootstraps the initial `main` revision only if its `cinema-client` CI check passed. Subsequent updates require a merged, associated APIShield PR, the unchanged validated PR head, successful CI on its exact merge SHA, and matching live provider hashes. It polls every 10 seconds and deploys only the current eligible main revision. It does not run unmerged branches or merge PRs.

Releases have separate environments; provider databases stay outside them. Revision/instance health and a booking in an isolated `smoke-` show namespace verify a new release. Failed verification restores the previous release and publishes failure evidence. Restoring old code does not claim compatibility with a new provider API.

## LAN configuration

On B run `ipconfig` and identify the active Wi-Fi IPv4 address. Both computers must use a Private Windows network. If provider ports are blocked, use Windows Defender Firewall → Advanced settings → Inbound rules → New rule → TCP ports 8101 and 8102, restricted to the Private profile and local subnet. Do not disable the firewall. Add 8100 only if A needs to open the client over LAN. Provider admin mutations remain loopback-only; use B's client provider tab.

Confirm A can reach `http://B_ADDRESS:8101/health` and `http://B_ADDRESS:8102/openapi.json` using its browser or `Invoke-RestMethod` with the actual address substituted. APIShield remains loopback-only on A; no tunnel, remote browser admin, or inbound deployment callback is needed.

## System A: real monitoring and automation

After the client baseline is merged and A has a clean local checkout of it:

```powershell
./demo/scripts/start_system_a.ps1 -ClientRepository C:/APIShieldDemo/client-source -ProviderHost 192.168.1.20 -Model gemini-3.8-flash
```

The address in this example must be replaced by B's actual Wi-Fi address. The script registers `cinemaflow`, `cinema-theatre`, and `cinema-payment` in the existing private APIShield job registry, with five-minute real monitoring and explicit LAN-source permission. It refuses to overwrite an existing CinemaFlow registration. The model identifier is configurable; the live qualification records in reports/demo-verification-2026-10-19 document the model actually exercised on this development machine.

Start APIShield with `start_app.bat`, select CinemaFlow Integration, and choose Check now for immediate rehearsal. The parent overview shows both provider states, endpoint inventory, combined semantic graph, and a manual/automatic mode selector. Manual is the default. Manual mode detects automatically if monitoring is enabled, but requires Ask AI to Update and explicit publication. Automatic mode generates/validates/publishes a PR; it never merges it.

Connect the existing GitHub publication panel to `Surjithk73/APIGuardTesting`, branch `main`, before enabling automatic mode. Every model candidate still runs in a temporary workspace through APIShield's existing validation engine. Failed jobs require an explicit retry rather than billing a new request on every poll.

## Reset a rehearsal

Stop System B first, then run:

```powershell
./demo/scripts/reset_rehearsal.ps1
```

This resets only the named managed provider SQLite databases to V1 and clears demo bookings/payments. It preserves unrelated files and never resets client source or rewrites Git history. To repeat a V1-client migration, use a new clean checkout of the recorded baseline commit and publish the next demo cycle through a normal forward commit/PR. Do not force-push main. Starting services alone preserves the active provider versions.

Nondefault ports: both PowerShell launchers accept `-ClientPort`, `-TheatrePort`, and `-PaymentPort`. Use the same three distinct ports on A and B. In reviewed-merge mode, B reads the ports from `client_port` and the two provider URLs in its private deployment JSON instead; those settings take precedence over launcher port flags. Adjust the Private-profile firewall rule accordingly.
