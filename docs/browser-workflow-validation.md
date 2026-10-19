# Browser workflow validation — 12 October 2026

The local browser application is complete for the approved scope: direct access without authentication, repository onboarding, saved contract updates, scans/comparisons/repairs, persistent run history, cancellation, evidence review and patch/report downloads. Default frontend is the integration workspace; the payment demonstration is separate.

## Verification

| Check | Observed result |
| --- | --- |
| Full offline Python suite, credentials empty | 205 passed, 1 skipped, 1 dependency deprecation warning in 96.94 seconds |
| Frontend tests | 8 passed |
| Production frontend build | Passed, final main bundle 362.89 kB / 113.58 kB gzip |
| Frontend lint | Exit 0; no new workspace warnings, six existing legacy demonstration warnings |
| Focused browser backend/adapter tests before final review | 17 passed |
| Final review regressions | Missing dependency setup and invalid-key redaction: RED 2 failed → GREEN 2 passed; selection generations and malformed history fallback: RED → GREEN frontend suite |
| One-click launcher | Actual start/stop process-tree cycle passed; server serves built frontend on 127.0.0.1:8002 |
| Browser operation | Shipping setup, code scan, contract comparison, real offline repair, patch preview/download, saved integration registration/edit, invalid repository error and actual cancellation passed |
| Restart | Registry and the three prior shipping jobs retained across real server restarts; a later cancellation persisted its own terminal report |
| Design review | ship; desktop/mobile, onboarding and settings captures approved, no material design fixes |
| Source integrity | Real shipping repair left committed src/tests unchanged; patch independently applicable; disposable workspace removed |

Python 3.13.3 and Node 26.5.0 on Windows. The skip requires POSIX executable semantics; Windows exercised the cross-platform restoration case. Starlette reports a dependency deprecation for an AnyIO alias. New launcher failure coverage invokes Windows PowerShell explicitly with an empty Python environment, reproducing the real BAT entry point. Existing engine wrong-repair, integrity, cancellation and deadline tests passed in the full suite.

## Independent review corrections

A fresh whole-change reviewer found four concrete defects; all were fixed in one regression-driven pass:

- Report/patch responses arriving after another run is selected are discarded using selection generations, including returning to the same run. Component unmount invalidates outstanding selection evidence.
- Dependency probing exits silently when imports are absent, allowing Windows PowerShell to reach installation rather than stop on a redirected traceback.
- Minimal failed persisted job records render as a Run with the actual diagnostic rather than crash history by indexing an absent operation.
- Model-key validation errors suppress submitted input; valid and invalid responses do not echo the key.

Earlier browser acceptance also reproduced a report-reader/startup-lock race. Untouched queued reports now read state without taking the worker execution lock; genuine owned-job recovery retains its prior locking behavior. The real shipping browser acceptance and full suite passed afterward.

## Product and design boundaries

This is a usable local application, not the entire seven-phase roadmap. No accounts or authentication were added, as requested. The launcher binds to loopback. Browser onboarding accepts local paths, JSON OpenAPI uploads and fixed pytest configuration; arbitrary setup/test argv remains a trusted server/CLI configuration capability. Failed edits leave the last valid configuration published; jobs retain their original configuration/contract snapshots. Model keys entered in Settings live in server memory only, and external launch-environment keys follow that environment's lifetime.

The user authorized a UI/UX revamp; the replacement operating workspace uses existing React and Lucide with CSS/native controls, adding no frontend runtime dependencies. PRODUCT.md, DESIGN.md, .impeccable/design.json and the surface direction contract capture the shipped system. Code was formatted using a temporary Prettier command, not a new application dependency. Mechanical design detection ran once; its unused Inter declaration warning was removed. Six actual desktop/mobile/form/settings screenshots were independently reviewed. One mobile full-page capture was recaptured at scroll position zero to remove a fixed-element capture artifact; no style change was needed.

Live Gemini quality and paid transport were not exercised. Original checkouts were not merged into or edited. GitHub App proposals, explicit behavioral-requirement research, benchmarks, hosted workers/scheduling and external deployment remain later work. Native oasdiff is already installed on this machine; fresh machines must satisfy the documented prerequisite. Multi-server shared-registry coordination is outside this single local-server scope.

## Start using it

Open start_app.bat in the attached ProjectSeven worktree, or visit http://127.0.0.1:8002 while the server is running. Select shipping-example and use Scan code, Compare contracts or Try example repair. For personal projects, Connect integration and upload the two contracts. Settings enables session-only AI generation. Use stop_app.ps1 before restarting the server. Logs are under .app-logs; source workspaces/evidence/registry default to ~/.apishield/jobs.
