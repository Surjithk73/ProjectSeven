# Run the current demo on another Windows laptop

Use this guide when moving the **host** to another Windows 10/11 x64 laptop. That laptop runs APIShield, CinemaFlow, IMAX, GPay and the deployment helper. A phone or another computer only needs a browser on the same reachable Wi-Fi/LAN. Internet access is also needed for GitHub and Gemini. No local GPU, Docker, phone installation or second server is required for this setup.

## 1. Know which repository to use

| Repository | Purpose |
|---|---|
| https://github.com/Surjithk73/ProjectSeven | APIShield, simulated providers, launch/reset tools and this guide |
| https://github.com/Surjithk73/APIGuardTesting | CinemaFlow client, client CI and generated migration PRs |

Clone **ProjectSeven**, branch **feature/cinemaflow-multi-provider**. The launcher clones the client repository itself; you do not need to set up a second checkout manually. Do not assume ProjectSeven's `main` contains this branch's newest changes.

GitHub does not contain your Python environment, installed frontend dependencies/build, downloaded oasdiff executable, service-account credential, active demo databases or previous local job history. Recreate dependencies on the new laptop. Transfer the authorized Google service-account JSON privately; never upload it to either repository, include it in a PR or paste it into chat.

## 2. Install prerequisites on the new host

Install Git, GitHub CLI, Python 3.13 and Node.js LTS (22.12 or newer). The development host used Python 3.13.3; the repository also declares Python 3.11+ support. Run these commands in PowerShell if Windows Package Manager is available:

```powershell
winget install --exact --id Git.Git
winget install --exact --id GitHub.cli
winget install --exact --id Python.Python.3.13
winget install --exact --id OpenJS.NodeJS.LTS
```

Complete installer prompts. Close PowerShell and open a **new PowerShell window** so installed tools appear on PATH. Verify:

```powershell
git --version
gh --version
py -3.13 --version
node --version
npm.cmd --version
```

If a tool is not found, finish its installation or add it to PATH before continuing. If `winget` is unavailable, use the official installers from https://git-scm.com/downloads/win, https://cli.github.com/, https://www.python.org/downloads/windows/ and https://nodejs.org/en/download. Python should include its launcher; Node should include npm. The commands below use `npm.cmd` to avoid PowerShell's script execution-policy restriction.

## 3. Clone the current branch and prepare dependencies

The following chooses `ProjectSeven` under the new Windows user's profile. Choose an empty location; if that folder already exists, inspect it instead of overwriting it.

```powershell
Set-Location $env:USERPROFILE
git clone --branch feature/cinemaflow-multi-provider --single-branch https://github.com/Surjithk73/ProjectSeven.git ProjectSeven
Set-Location ProjectSeven

py -3.13 -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt

npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run build
```

Run each command only after the preceding command succeeds. Do not copy `venv` or `node_modules` from the old laptop; their installation paths and executables can differ. The CinemaFlow client release gets its own dependencies automatically during deployment. You do not need `npm run dev` or the older SwiftPay/banking launcher for this demo.

## 4. Install native oasdiff

Contract comparison needs the separate oasdiff executable, which is intentionally excluded from Git. The following installs **v1.30.0**, matching the tested Windows demo tool, from its official release and verifies the archive checksum before extraction. These commands assume an Intel/AMD x64 laptop; a Windows ARM64 host needs the matching upstream ARM64 asset and separate verification.

Run from the ProjectSeven folder:

```powershell
New-Item -ItemType Directory -Force .apishield/install/oasdiff | Out-Null
gh release download v1.30.0 --repo oasdiff/oasdiff --pattern oasdiff_1.30.0_windows_amd64.tar.gz --pattern checksums.txt --dir .apishield/install/oasdiff

$assetLine = Get-Content .apishield/install/oasdiff/checksums.txt | Where-Object { $_ -match '\soasdiff_1\.30\.0_windows_amd64\.tar\.gz$' }
if (-not $assetLine) { throw 'Archive checksum is missing' }
$expectedHash = ($assetLine -split '\s+')[0]
$actualHash = (Get-FileHash .apishield/install/oasdiff/oasdiff_1.30.0_windows_amd64.tar.gz -Algorithm SHA256).Hash
if ($actualHash -ne $expectedHash) { throw 'Archive checksum mismatch; do not extract or run it' }

New-Item -ItemType Directory -Force tools | Out-Null
tar -xzf .apishield/install/oasdiff/oasdiff_1.30.0_windows_amd64.tar.gz -C tools oasdiff.exe
.\tools\oasdiff.exe --version
```

If GitHub CLI requests login before the public download, complete step 5, then return here. If files from an earlier download already exist, inspect and reuse the verified files rather than repeatedly downloading over them. The phone launcher discovers `tools/oasdiff.exe` automatically.

## 5. Connect GitHub on the new host

The existing phone-demo profile expects **Surjithk73** as the publisher/deployment account. Sign in on the new laptop using GitHub CLI's browser/device flow:

```powershell
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
gh api user --jq .login
gh repo view Surjithk73/APIGuardTesting --json nameWithOwner,viewerPermission
```

Confirm the returned username is `Surjithk73` and repository permission permits writing. Sign into the **phone browser** as **surjk73** for independent review and merge. These are separate sessions: do not change the host's CLI login to the reviewer account. Existing collaborator access remains valid; it does not need to be invited again for a new laptop. Do not share passwords, tokens or device-login codes in chat.

## 6. First launch and Google connection

1. In File Explorer, open the cloned ProjectSeven folder and double-click **Start Phone Demo.bat**. Keep its console open. Initial startup downloads the client and installs a release environment, so the first start can take several minutes.
2. Wait until the console prints the laptop dashboard URL and phone links. APIShield normally opens at `http://127.0.0.1:8005/?project=cinemaflow`; use the printed dashboard URL if that port is already occupied. CinemaFlow is `http://127.0.0.1:8100` on the host.
3. In APIShield, open **Settings → AI connection**. Select the privately transferred, authorized service-account JSON, choose **Save service account**, then **Test connection**. Wait for success. Internet access, active Google billing, the configured API and service-account permissions must still be available. Cloning GitHub does not transfer any of those credentials or permissions.
4. APIShield stores its managed credential under the new Windows user's private `%USERPROFILE%\.apishield\credentials\service-account.json` directory, outside Git. It loads automatically on later starts. Do not create an API key or `.env` key as a replacement.
5. After this first successful initialization, double-click **Stop Phone Demo.bat**, then **Reset Phone Demo.bat**. Wait for **Complete reset finished**, then run **Start Phone Demo.bat** again. This creates a fresh V1 rehearsal branch for the new host, independent of earlier trials. Do not run reset before a managed demo workspace has been initialized by its first launch.

Run only one host for a given rehearsal. Stop the old laptop's demo before presenting from the new one. The new host's saved private credential survives the complete demo reset.

## 7. Open the phone or audience laptop

Connect the browser device and the host to the same non-isolated Wi-Fi/LAN. Open the host's **current printed Wi-Fi link**, for example `http://<current-host-Wi-Fi-IPv4>:8100`. Do not type `127.0.0.1` on the phone: that points to the phone itself. Do not reuse the old laptop's IP address. Hostname links may work, but the active Wi-Fi IPv4 is the usual fallback. Ignore VPN, WSL and virtual-adapter addresses.

If the page cannot open, check guest-network/client isolation and allow inbound **TCP 8100 only on the Private network/local subnet** in Windows Defender Firewall. Do not disable the firewall or expose APIShield/provider administration publicly. APIShield and provider services remain local to the host; only the client browser port is shared. A shared internet connection across different networks is not a LAN connection; public internet hosting/tunnelling is not included here.

## 8. Present the full flow

1. Confirm IMAX and GPay are V1. On the phone, select a show and seats, pay, and show a successful booking.
2. On the host's CinemaFlow **API providers** tab, switch **one provider** to V2. IMAX changes can break seat/booking behavior; GPay changes leave selection available but the old payment client shows **Payment failed** at checkout.
3. On APIShield, choose the affected provider or CinemaFlow and **Check for API Changes**. Show changed endpoints and affected graph nodes.
4. Choose **Ask AI to update**. Show **Agent activity**, validation, and the proposed code changes. The current guided demo includes prewritten reference patches in the AI system prompt; keep it separate from unseeded research results.
5. Choose **Prepare draft preview**, then **Publish GitHub PR**. On the phone, sign in as `surjk73`, inspect the changes/checks, mark the draft ready if necessary, and merge the generated PR into the **rehearsal branch printed by the launcher**.
6. Leave the host launcher running. Wait for **Deployed and verified** in APIShield, then refresh the phone and repeat the previously failing action. Merging alone is not the final deployment signal.
7. GitHub may offer **Compare & pull request** to merge the rehearsal branch into `main`. Ignore that suggestion. No second PR is needed. `main` intentionally remains the baseline while the demo follows its rehearsal branch.

Manual mode requires requesting generation/publication. Automatic mode may generate, validate and publish automatically; it still requires the person's review and merge.

## 9. Stop and repeat

- **Stop only:** double-click **Stop Phone Demo.bat**. Provider data and demo history remain available for a restart.
- **Start over completely:** double-click **Reset Phone Demo.bat**, wait for completion, then **Start Phone Demo.bat** and refresh both browser pages. Reset stops the managed services itself.
- **GitHub cleanup:** none is required between trials. Reset creates a fresh rehearsal branch from the verified V1 baseline and archives the previous local state. Old merged PRs/branches remain history. Do not delete or force-reset `main`.
- **Update the new host later:** stop the demo, run `git pull --ff-only` in this ProjectSeven branch, reinstall changed Python dependencies and rebuild the frontend if its source changed, then restart. This is updating APIShield itself; it is separate from the automatic deployment of a merged CinemaFlow migration PR.

All generated demo state stays under this checkout's `.apishield/cinema/`. Python/Node/Git/GitHub CLI installations and the private credential are machine-local prerequisites. Other existing project documentation describes older banking or two-server setups; use this guide and [PHONE-DEMO.md](PHONE-DEMO.md) for the laptop-hosted CinemaFlow demonstration.
