# Browser Workflow Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline and a fresh whole-branch reviewer.

**Goal:** Operate APIShield through a complete local browser interface.
**Architecture:** Existing React routes call existing job endpoints plus minimal local onboarding APIs. Atomic filesystem registry reuses JobStore storage; no database or new UI dependencies.
**Spec:** ../specs/2026-10-12-browser-workflow-design.md

## Review Focus
- Remote or foreign-origin clients cannot register executable local integrations.
- Repository containing job storage is rejected before saving configuration.
- Browser cannot select an arbitrary offline patch path or replace server allowlist entries.
- Polling failures surface recovery; failed jobs cannot look validated or expose patch actions.
- Example and user source remain unchanged after repair and history survives restart.

## Task 1: browser onboarding and example
Files: apishield/browser_setup.py, dashboard_jobs.py, dashboard_api.py; tests/test_browser_setup.py.
Interfaces: GET /api/workspace returns model_available and integration details; POST /api/integrations accepts strict name/repository/code_paths/test_path/base_spec/target_spec; POST /api/examples/shipping creates the known offline fixture. JobRequest proposal model|example defaults model; only example integration maps to server candidate.
- [x] RED tests: register valid Git source and reload registry; reject source-root storage, remote Origin, arbitrary argv; real shipping example repair validates and patch is retrievable.
- [x] Implement minimal persistence/registration and fixed candidate selection; GREEN focused tests.
- [x] Commit and record evidence.

## Task 2: usable browser workspace
Files: frontend/src/App.jsx, pages/Workspace.jsx, workspace.js, workspace.css, tests/workspace.test.js; preserve legacy routes.
Interfaces: shared JSON request helper throws HTTP errors; presentation derives success only from actual validated status. Browser state consumes real workspace/jobs/report endpoints, refreshes bounded intervals and supports onboarding, cancellation and patch preview/download.
- [x] RED frontend helper tests: HTTP errors, missing/failed validation and job sorting.
- [x] Implement responsive workspace, integration form, actionable reports/history; GREEN tests/build/lint.
- [x] Exercise real browser flow at desktop/mobile widths and inspect screenshots in one batch; fix material defects once.

## Task 3: launch and verification handoff
Files: start_app.ps1, start_app.bat, README.md, docs/browser-workflow-validation.md.
- [x] Provide one-click local launcher checking ports/dependencies and opening the real app; preserve existing demo launcher.
- [x] Run full suite, frontend checks, real browser workflow and independent final/design review; fix Important issues with regressions.
- [x] Commit and keep attached worktree; leave app running and open it for the user.
