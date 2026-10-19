# GitHub accounts for the proposed two-machine demo

## Confirmed on System A

On 2026-10-19, `gh api user --jq .login` returned `Surjithk73`. Repository inspection returned ADMIN permission and `main` as the default branch for both `Surjithk73/ProjectSeven` and `Surjithk73/APIGuardTesting`. Both repositories were public at inspection time. No login replacement is needed on A now.

ProjectSeven holds APIShield and its supporting project files. APIGuardTesting will hold the deployed movie client. Creating this document does not provision or deploy that client.

## Details to provide

- The reviewer account's GitHub username or profile URL. In GitHub, select the avatar at the top right, choose Your profile, and copy the profile URL.
- Confirmation the reviewer accepted the invitation to APIGuardTesting.
- The GitHub username used by the deployment helper on B, if different from the reviewer. The planned helper posts deployment evidence and therefore needs repository write access; read-only anonymous cloning alone is insufficient for that role.
- Later, B's active Wi-Fi IPv4 address and chosen installation directory for service setup.

Passwords, personal access tokens, service-account JSON, private keys, and browser/device login codes are not needed in chat or committed files.

## Invite the reviewer

The owner opens `https://github.com/Surjithk73/APIGuardTesting/settings/access`, selects Add people, enters the reviewer's username, and sends the invitation. The reviewer signs into their own account and accepts it. The publisher should not use the reviewer's login; the separate account reviews the publisher's PR and merges it after checks pass.

## Authenticate the helper on B locally

After installing GitHub CLI, run these in PowerShell on B and complete the browser login using the intended local account:

```powershell
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
gh api user --jq .login
gh repo view Surjithk73/APIGuardTesting --json nameWithOwner,viewerPermission,defaultBranchRef
```

Share only the returned username and whether repository access succeeded. Keep authentication material in the local credential store. A third account is optional: for this demo B's reviewer account can also post deployment evidence. Configure its username as the allowed deployment author; do not accept arbitrary comments as proof of deployment.

## Network details on B

```powershell
ipconfig
```

Read the IPv4 Address under the connected Wireless LAN adapter Wi-Fi. Use that address in the private local setup configuration on A; do not put personal LAN addresses into the shared default configuration. The planned setup checks service ports and reachability before attempting a rehearsal.

## Official references

- GitHub CLI browser authentication: https://cli.github.com/manual/gh_auth_login
- Personal-repository collaborator invitations: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository
- Reviewing a PR and the restriction on approving one's own PR: https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews
