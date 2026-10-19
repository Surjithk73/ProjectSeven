# GitHub accounts for the proposed two-machine demo

## Confirmed on System A

On 2026-10-19, `gh api user --jq .login` returned `Surjithk73`. Repository inspection returned ADMIN permission and `main` as the default branch for both `Surjithk73/ProjectSeven` and `Surjithk73/APIGuardTesting`. Both repositories were public at inspection time. No login replacement is needed on A now.

ProjectSeven holds APIShield and its supporting project files. APIGuardTesting will hold the deployed movie client. Creating this document does not provision or deploy that client.

## Details to provide

The reviewer is now `surjk73` (`https://github.com/surjk73`), replacing the previously proposed account. On 2026-10-19, the owner sent invitation `338492013` with write permission to `Surjithk73/APIGuardTesting`. Acceptance has now been verified through GitHub: `surjk73` has the `write` role, and the invitation is no longer pending. No collaborator access was granted to the previously proposed reviewer.

- The GitHub username used by the deployment helper on B, if different from the reviewer. The planned helper posts deployment evidence and therefore needs repository write access; read-only anonymous cloning alone is insufficient for that role.
- When B is available, copy the HTTP link its launcher prints. No IP address is required in advance. Keep the checkout and all demo folders under its ProjectSeven folder.

Passwords, personal access tokens, service-account JSON, private keys, and browser/device login codes are not needed in chat or committed files.

## Reviewer access and initial client PR

Collaborator setup is complete. [Client setup PR #2](https://github.com/Surjithk73/APIGuardTesting/pull/2) is ready for review, and `surjk73` is its requested reviewer. Both `cinema-client` checks passed on head `1403ea98cb67a4a37cc87c74fc872431920fb098`. Sign in as `surjk73`, inspect the files and checks, approve, then merge when satisfied. The publisher account must not approve its own PR. No automatic merge has been performed.

## Authenticate the helper on B locally

After installing GitHub CLI, run these in PowerShell on B and complete the browser login using the intended local account:

```powershell
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
gh api user --jq .login
gh repo view Surjithk73/APIGuardTesting --json nameWithOwner,viewerPermission,defaultBranchRef
```

Share only the returned username and whether repository access succeeded. Keep authentication material in the local credential store. A third account is optional: for this demo B's reviewer account can also post deployment evidence. Configure its username as the allowed deployment author; do not accept arbitrary comments as proof of deployment.

## Connection link on B

Run `./demo/scripts/start_system_b.ps1` from the ProjectSeven checkout. It prints the current machine's HTTP client link. Copy that into A's setup prompt. Use `./venv/Scripts/python.exe -B -m demo.setup connection-info` for detected LAN alternatives. This discovery happens on the selected computer when the demo starts, so its future IP/name need not be supplied beforehand.

## Official references

- GitHub CLI browser authentication: https://cli.github.com/manual/gh_auth_login
- Personal-repository collaborator invitations: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository
- Reviewing a PR and the restriction on approving one's own PR: https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews
