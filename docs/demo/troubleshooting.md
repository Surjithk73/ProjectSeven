# CinemaFlow failure diagnosis

| Symptom | What to check |
|---|---|
| Provider unreachable | B runtime logs, Wi-Fi IPv4, Private network firewall rules, and `/health` on each provider |
| V2 booking fails | Expected before migration; check both provider contracts in APIShield rather than switching the client to a prewritten compatibility adapter |
| Automatic mode rejected | AI connection, enabled real monitors, and connected GitHub target are prerequisites |
| Client checkout has changes | Preserve or commit user work; APIShield will not discard it or silently reset the checkout |
| New proposal supersedes old one | Another provider or source revision changed; the pending changes must be validated together |
| Google timeout/check generation failure | Agent activity retains the actual phase and test output; Retry is explicit, bounded, and may incur another AI request |
| PR open, no deployment | Human review/merge is mandatory; marking a draft ready is a GitHub action before merging |
| Merged but waiting | `cinema-client` must succeed on the exact merge revision, not only a PR test merge or an older head |
| Deployment failure | Private release journal and client log show preparation/health/smoke failure; old release is restored where possible |
| Running revision not accepted by A | Receipt author, workflow ID, provider hashes, merge SHA and smoke evidence must all match |
| No automatic retry | Failed workflows deliberately stop to avoid repeated paid requests and duplicate side effects |

GitHub publication, merge, deployment and verification are distinct statuses. A green unit-test run alone never means the live client has been updated.
