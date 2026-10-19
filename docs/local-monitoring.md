# Monitor an API contract locally

Start APIShield with `start_app.bat` in this worktree and open http://127.0.0.1:8002. Connect a local Git repository and two JSON OpenAPI contracts, then select that integration. The built-in example and externally managed integrations are read-only; a browser-connected integration has editable monitoring controls.

In **Settings → Project settings → Monitoring**, enter the provider's OpenAPI JSON URL, choose an interval (60 minutes by default, minimum 5 minutes), and choose the initial baseline:

- **Saved current contract:** compare downloads with the contract you uploaded as the current version. This can reveal changes that already happened before monitoring started.
- **First download:** establish the downloaded version as the baseline. Initialization creates no change alert.

Enable monitoring. APIShield must remain running on this computer for scheduled checks. Restarting restores saved schedules and evidence; missed intervals coalesce into one check, rather than a burst. **Check now** runs immediately, including when paused. **Pause** stops automatic checks; **Resume** enables them again. Different checks of one integration cannot overlap. Changing a source or baseline choice starts a new baseline and preserves historical evidence.

Use HTTPS sources normally. A trusted local/private-network source, including HTTP, requires the explicit opt-in. Unspecified, multicast and link-local/metadata destinations remain blocked. Every DNS destination/redirect is checked, connections use the checked IP while HTTPS verifies the original hostname, and each fetch is bounded by 15 seconds and 2 MiB. Fetches do not inherit proxies, cookies, GitHub credentials or Gemini keys. URLs cannot include embedded credentials or secret query parameters. Authenticated contract sources and YAML are outside this increment; no URLs referenced inside a downloaded contract are automatically fetched.

## Review a change

Downloads are retained as immutable snapshots. Whitespace and object-key order do not create a change; meaningful array order remains significant. Repeated observations of the same baseline/target reuse the existing change and comparison job.

**View evidence** opens the normal comparison report, including supported affected calls and declared requirement relationships. Comparisons use committed code, not uncommitted edits. **Rescan code** explicitly compares the retained contracts against a fresh committed source revision and the current integration configuration; earlier job IDs/evidence remain retained. Comparison completion does not mean code was repaired or tests passed.

**Accept as baseline** asks for confirmation, then makes that downloaded version the reference for future checks. It acknowledges a contract version; it does not modify, repair or validate your repository. A failed fetch or comparison never advances the baseline automatically.

**Request repair** is a separate explicit action on a retained change. It uses the retained comparison configuration/commit/contracts and the normal guarded engine. Configure an AI connection in **Settings → AI connection** first. Automatic monitoring never generates model candidates or publishes a PR. The Google Cloud connection supports an explicit connection test and paid repair requests; monitoring itself makes no AI request.

## Recovery and evidence

Errors preserve the previous successful observation and baseline. Correct the source, use **Check now**, or edit/save settings. Stale edits return a conflict, even after background polling: use **Reload monitoring** before retrying; this deliberately reloads saved settings rather than silently overwriting another edit. An interrupted fetch can be checked again after process loss/shutdown. An interrupted reserved comparison remains associated with its original identity as failed evidence; **Rescan code** creates fresh comparison evidence explicitly. Configuration preparation failures are also visible and follow the normal interval, rather than retrying every second.

Records live under the external job root (normally `C:/Users/surji/.apishield/jobs`): `_monitoring/<integration>/state.json` contains monitoring state, and `snapshots/` contains retained downloads. Comparison and repair evidence use ordinary job directories. Do not manually overwrite snapshots: integrity checks reject altered content. Back up this directory if you need to preserve local history. For a corrupt monitor record, preserve its files and correct the record rather than silently resetting a baseline.

Browser mutations are restricted to browser-connected integrations and the existing local origin/host/peer policy. Trusted server code can configure externally managed integrations through `jobs.monitoring.configure(name, settings, expected_revision)`; the browser continues to display them read-only. This local source policy is not a claim of hardened multi-tenant hosted fetching.
