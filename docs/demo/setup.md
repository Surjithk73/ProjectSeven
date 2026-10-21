# CinemaFlow two-machine setup

For the simpler laptop-hosted demo with a phone browser, use [PHONE-DEMO.md](PHONE-DEMO.md). The setup below remains available when a second Windows machine actually hosts the client and providers.

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
./venv/Scripts/python.exe -m demo.setup export-client --repository .apishield/cinema/client-source
```

Create a setup branch, commit those additions, run `python -m pytest movie_booking/tests -q` from the client checkout, and publish its PR. Once reviewed and merged, clone/pull `main` separately on A and B. APIShield's repair source must match the GitHub publication base exactly. Do not develop directly inside a deployed release directory.

## Quick single-computer development preview

```powershell
./demo/scripts/start_system_b.ps1
```

Open `http://127.0.0.1:8100`. Book a seat on V1, then use the API providers tab to switch payment or theatre to V2. Booking failures are expected until the corresponding adapter is updated. This preview serves the V1 source template directly; it is not the GitHub deployment rehearsal.

Stop using `./demo/scripts/stop_system_b.ps1`. The runtime owns only its child processes; Windows job objects include deployment descendants. Logs are in the private state directory, not in Git.

## System B: reviewed-merge deployment

All new demo folders stay inside this ProjectSeven checkout. Copy `demo/deployment/system-b.example.json` to `.apishield/cinema/system-b.json` (create that local directory first). The default relative `releases` path resolves inside ProjectSeven. Set `releases` to an empty dedicated folder inside this checkout and confirm `deployment_actor` matches B's GitHub CLI login. Sign in locally using the instructions in `github-accounts.md`. No credential belongs in that JSON.

```powershell
./demo/scripts/start_system_b.ps1 -DeploymentConfig .apishield/cinema/system-b.json
```

The helper explicitly bootstraps the initial `main` revision only if its `cinema-client` CI check passed. Subsequent updates require a merged, associated APIShield PR, the unchanged validated PR head, successful CI on its exact merge SHA, and matching live provider hashes. It polls every 10 seconds and deploys only the current eligible main revision. It does not run unmerged branches or merge PRs.

Releases have separate environments; provider databases stay outside them. Revision/instance health and a booking in an isolated `smoke-` show namespace verify a new release. Failed verification restores the previous release and publishes failure evidence. Restoring old code does not claim compatibility with a new provider API.

## Connection links — no IP needed in advance

On whichever Windows computer becomes System B, run the launcher from the ProjectSeven folder. It prints a computer-name link and records all detected LAN alternatives under `.apishield/cinema/providers/connection-info.json`:

```powershell
./demo/scripts/start_system_b.ps1
./venv/Scripts/python.exe -B -m demo.setup connection-info
```

The first command above previews the V1 template. For reviewed-merge deployment, pass `-DeploymentConfig .apishield/cinema/system-b.json` after the baseline PR is merged and B is authenticated. Open the printed client link once startup completes. Copy the computer-name HTTP link to A. If Windows hostname lookup is unavailable, use one of the printed IPv4 alternatives belonging to B's active Wi-Fi adapter. VPN/virtual-adapter alternatives may not be reachable from A.

Both machines must have direct LAN access; a shared internet connection alone is insufficient if they are on different or isolated networks. The HTTP links are LAN links, not public hosted URLs. Internet access across different networks would require a separately configured tunnel or hosted services; none is provisioned here.

Use a Private Windows network. If ports are blocked, use Windows Defender Firewall → Advanced settings → Inbound rules → New rule → TCP 8100, 8101 and 8102, restricted to the Private profile and local subnet. Do not disable the firewall. Provider admin mutations remain loopback-only; change versions using B's client provider tab. No firewall rule is changed automatically.

## System A: paste the client link

After the initial client PR is merged, clone its main branch into the ignored project-local source directory:

```powershell
New-Item -ItemType Directory -Force .apishield/cinema | Out-Null
git clone https://github.com/Surjithk73/APIGuardTesting.git .apishield/cinema/client-source
./demo/scripts/start_system_a.ps1
```

The launcher asks for the CinemaFlow HTTP link printed on B. It accepts a computer name or a copied HTTP origin and verifies that it resolves to LAN IPv4 addresses. There is no machine-specific IP committed to source. Custom provider ports can be passed with `-TheatrePort` and `-PaymentPort`; the copied client's port is used for its client link.

The A launcher registers the project with jobs under `.apishield/cinema/jobs`, then starts APIShield using that same job directory. Stop an already running port-8002 instance yourself before launching; it does not kill existing applications. Use `-SetupOnly` to register without starting. Reopen the configured workspace with `./demo/scripts/open_system_a.ps1`; optionally select `-Port 8005` if 8002 is occupied. This cinema launcher does not reset the banking demo. New demo logs, provider databases, release environments, caches and temporary files stay under ProjectSeven. Explicit demo paths outside the checkout are rejected. Existing managed AI credentials are read from their established location; they are not copied or moved.

Monitoring defaults to five minutes; use Check now for immediate checks. Manual mode requires Ask AI to Update and explicit publication. Automatic mode generates/validates/publishes a PR; human review and merge remain required. Connect the existing GitHub panel to `Surjithk73/APIGuardTesting`, branch `main`, before enabling automatic mode. Failed jobs require an explicit retry rather than a new paid attempt on every poll.

## Reset a rehearsal

Stop System B first, then run:

```powershell
./demo/scripts/reset_rehearsal.ps1
```

This resets only the named managed provider SQLite databases to V1 and clears demo bookings/payments. It preserves unrelated files and never resets client source or rewrites Git history. To repeat a V1-client migration, use a new clean checkout of the recorded baseline commit and publish the next demo cycle through a normal forward commit/PR. Do not force-push main. Starting services alone preserves the active provider versions.

Nondefault ports: both PowerShell launchers accept `-ClientPort`, `-TheatrePort`, and `-PaymentPort`. Use the same three distinct ports on A and B. In reviewed-merge mode, B reads the ports from `client_port` and the two provider URLs in its private deployment JSON instead; those settings take precedence over launcher port flags. Adjust the Private-profile firewall rule accordingly.
