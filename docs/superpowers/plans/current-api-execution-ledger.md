# Current API implementation ledger

Execution method: native, approved 2026-10-14. Spec and plan approved. All implementation remains in primary ProjectSeven; no commits or branch changes.

Ruling: reuse the authoritative primary checkout with its existing uncommitted app changes, rather than isolate from an old Git HEAD — user explicitly moved development here and approved direct execution of this plan; copying only committed state would omit the application being changed.

Live AI: two minimal Gemini 3.8 Flash requests returned HTTP 503. Live generation is not verified.

Tasks 1-7 implemented in the primary checkout. Task 8 verification/docs complete except successful live AI and rendered-browser criteria, which remain blocked/unverified.

Task 1 RED: 3 failures for missing source_mode. GREEN: working snapshots plus existing engine tests passed (53 passed, 1 skipped). Added injection regression RED -> GREEN; retained inventory rejects extra files. Snapshot bounds: 4 MiB/file, 32 MiB total; dependency/secret trees excluded.

Task 2 RED: active docs endpoint missing/module absent. GREEN: V1 and V2 captured docs tests passed. Checking does not advance accepted state.

Task 3 RED: current overview endpoint 404. GREEN: uncommitted edits appear, neutral first overview and cache reuse pass. Current unresolved matching comparisons remain visible; stale historical graphs do not control fresh applied source.

Tasks 4-5 RED: intent module absent / engine lacked ai_intent. GREEN: separate generated-check validation and baseline-fail/postrepair-pass evidence passed. Browser example proposal rejected; existing CLI offline fixtures retained only for regression workflows. Ruling: infer executable checks during a relevant repair, not every idle page view — avoids repeated paid generation and unrelated generated-test artifacts. Overview automatically requests bounded business graph interpretation once per captured context.

Task 6 RED: local_apply module absent and interrupted Apply not recoverable. GREEN: no-commit Apply, stale user edit refusal, rollback, prepared-write retry and user-deletion refusal passed. Config metadata renamed from config_token to config_fingerprint because the existing credential redactor correctly strips token-named fields. Source-tree retries are pinned.

Task 7 RED: missing dashboardActions and stale-contract review remained visible. GREEN: primary action stable, review scoped to source and API/config fingerprints, larger primary controls, compact activity, always available overview actions, preset adapter control removed, manual rule/test setup removed from normal UI.

Fresh final reviewer found four defects: missing model connection on overview scans, concurrent automatic request duplication, stale dashboard review context and recovery overwriting a deleted source. One fix pass added failing tests and corrected all four; focused suite passed 18 tests. Recovery also reconciles applied/prepared manifests after interrupted writes.

Verification: broad affected backend selection 144 passed/1 skipped; focused final selection 18 passed; frontend 58 passed, build and lint completed (incumbent warnings). No Git commit, branch, push or PR created. Managed server restarted after confirming no queued/running jobs and verifying its PID command.

Actual HTTP: V1 check ea5229098f7a40a18093fa1370368968 returned completed with 0 changed operations and 0 affected calls; V2 check job 759c9041a60e4cffafe96473c812f1f5 returned completed with 4 changed operations and 3 affected calls. Provider restored to V1. Current overview job a00690b44251428ca5b728cc09739834 retained 45 graph nodes and a live Google service failure. The two earlier minimal requests returned HTTP 503. No successful live graph/intent/repair claimed.

Ruling: do not retry provider failures indefinitely or swap Gemini models silently — user pinned gemini-3.8-flash and asked for speed. Static functionality ships with clear AI errors; live AI acceptance remains pending actual provider access.
