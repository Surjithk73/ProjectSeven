# Run the laptop and phone demo

The Windows laptop hosts APIShield, CinemaFlow, both API providers and the deployment helper. The phone opens CinemaFlow and GitHub in its browser. It needs no developer tools or installation. Connect both devices to the same reachable Wi-Fi/LAN; being on the internet alone does not provide a connection between them.

## Start

1. On this laptop, double-click `Start Phone Demo.bat` in `C:/Users/surji/ProjectSeven`. Keep its console open or minimized. The existing Python environment, built frontend, Git and GitHub CLI are required on the laptop only.
2. The console prints the laptop dashboard address (normally `http://127.0.0.1:8005/?project=cinemaflow`) and opens it. Provider controls are in CinemaFlow's **API providers** tab at `http://127.0.0.1:8100` on the laptop.
3. On the phone, open the laptop's Wi-Fi address on port 8100. During verification it was `http://192.168.1.40:8100`; use the current address printed by the launcher if the network changes. The hostname alternative is `http://SK73:8100`, if your phone resolves it. Ignore addresses belonging to virtual adapters.
4. Keep GitHub CLI on the laptop signed in as `Surjithk73`. Sign into GitHub in the phone browser as `surjk73` to review and merge PRs.

If the phone cannot connect, check that both devices are on the same non-isolated network and Windows Firewall permits inbound client TCP port 8100 on the private network. The launcher does not change firewall settings. APIShield and provider administration remain bound to the laptop's loopback interface.

## One-time baseline review

The initial client is in [setup PR #2](https://github.com/Surjithk73/APIGuardTesting/pull/2). Review and merge it as `surjk73`, then wait for the `cinema-client` checks on the merged main commit to pass. Restart the launcher afterward.

While main does not contain this client, the launcher explicitly starts **preview mode** from `feature/cinemaflow-client`. Booking and provider controls are available, but GitHub publication is not connected and automatic deployment is not enabled. Once the baseline exists on main, startup connects the repository and selects merged-release deployment. The deployment helper still requires successful CI on the exact main commit before activation.

## Demonstrate a migration

1. Start with both providers on V1. Book seats on the phone and observe successful checkout.
2. On the laptop's provider tab, change the theatre or payment API to V2. Exercise the affected phone action to show the incompatible client behavior.
3. In APIShield, select CinemaFlow and **Check for API Changes**. Inspect the affected provider, endpoints and graph, then start the AI update. Agent activity shows generation and validation progress.
4. Review the validated candidate and prepare/publish its GitHub PR. Use the GitHub route for this demonstration rather than applying working files locally.
5. On the phone, inspect the PR and checks as `surjk73`, approve and merge it. A person always performs this step. In automatic edit mode APIShield may detect, generate, validate and publish automatically, but it still waits for a human merge.
6. Leave the laptop launcher running. After merge and successful CI, its deployment helper activates the exact merged commit, runs a smoke check and records deployment evidence. Refresh CinemaFlow on the phone and repeat the booking action.

This demonstrates a browser client on another device with deployment hosted on the laptop. The phone does not run a server or receive a Git checkout.

## Stop and retained files

Double-click `Stop Phone Demo.bat`. It requests shutdown of this launcher's owned services and leaves unrelated applications running. Restarting preserves provider data and run history; it does not silently reset the demo to V1. Select V1 explicitly for another rehearsal when appropriate.

## Complete reset, including after a merged migration

Double-click **Reset Phone Demo.bat**, wait for **Complete reset finished**, then double-click **Start Phone Demo.bat**. Refresh both browser pages after startup. The reset requests shutdown itself, so it can also be used while the phone demo is running. It does not start the demo automatically.

The equivalent command, from `C:/Users/surji/ProjectSeven`, is:

```powershell
.\venv\Scripts\python.exe -B -m demo.phone --reset
```

The reset restores both providers to V1 with empty payments/reservations, prepares the V1-compatible client at commit `0439f7c451dcc1032ed309071b0536ad2b12000b` (including the phone HTTP fix and IMAX/GPay labels), and starts with fresh APIShield state. On the next launch, APIShield initializes V1 contract baselines, manual mode, a clean graph/run history and a new GitHub publication target. The existing Google credential connection remains available.

Each reset creates a fresh GitHub branch named `demo/rehearsal-<UTC timestamp>-<unique suffix>` from that verified commit. New migration PRs target this branch, and deployment follows its human-reviewed merges. This makes a complete migration repeatable even after previous trials were merged; it does not rewrite `main` or remove old PRs/branches. Internet access and the laptop's `Surjithk73` GitHub CLI login are required. The launcher prints the current rehearsal branch so the reviewer can verify the PR destination.

Previous local state, logs, candidates, client source and releases are moved intact to `.apishield/cinema/phone-archives/<rehearsal identifier>/`. Archives accumulate; they are not silently deleted. A failed authentication/CI check or client download preserves the previous workspace. If shutdown cannot finish, reset refuses to move the running workspace. Other APIShield workspaces, the banking demo and academic artifacts are outside this reset.

The older `demo.setup reset --state .../providers` command still resets **providers only**. Use **Reset Phone Demo.bat** for the complete reset described here.

All new runtime files stay under `C:/Users/surji/ProjectSeven/.apishield/cinema/phone`: `profile.json`, `deployment.json`, `client-source/`, `jobs/`, `providers/`, `releases/` and `logs/`. Temporary files and caches stay under the project's `.apishield/cinema/` directory. The existing managed Google credential is read from its configured location and is not copied into the client or repository.

The previous two-Windows-machine option remains documented in [RUN-DEMO.md](RUN-DEMO.md).
