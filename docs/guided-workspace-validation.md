# Guided workspace verification — 2026-10-13

Scope: frontend navigation, information hierarchy, beginner copy and interactions. The Python engine and provider/publication interfaces are unchanged. This UI pass made no paid AI requests and no GitHub writes.

## Automated checks

- `npm --prefix frontend test`: 38 tests passed, including project-specific recommendations, internal verification filtering, native selected-tab visibility and distinct error recovery.
- `npm --prefix frontend run build`: production build succeeded.
- `npm --prefix frontend run lint`: six existing warnings in demo components/pages; no new warning in the guided workspace files.
- `git diff --check`: no whitespace errors.

The full Python suite was not rerun for this frontend-only change. The preceding backend publication stage recorded 426 passing tests and one skip.

## Browser checks

The production app was exercised using the in-app browser at desktop 1280×900, mobile 390×844 and the user's 648×704 viewport. Workspace, Results, GitHub review, Project setup and beginner guidance were captured and visually inspected. The page has no horizontal overflow at those widths. Result and setup tabs support keyboard navigation. Programmatic selection and resize keep the active mobile tab visible.

The supplied shipping example was compared and repaired offline through the UI. Repair job `109bd34064bd4ba6b46f6cbf6b2a206e` passed its configured tests and business-rule checks, and its patch loaded in Code change. This proves the supplied example workflow, not live model quality.

An unsaved GitHub target edit survived switching setup tabs and was restored without saving. The existing controlled draft PR remained attached to source repair `d2d449eceb534b15bac879a1656d10e3`; internal publication verification no longer appears as a separate user repair. Its remote state was not refreshed or changed during this pass.

A separate read-only local fixture served the retained example report with a synthetic patch 404. Dismissing the global action message left the inline failure and Reload patch visible. Reload patch explicitly retried and displayed the failure again. Production artifacts were not modified to create this failure.

## Design review

The Impeccable finish reviewer requested three material fixes: preserve original result identity, reveal selected mobile tabs, and distinguish failed actions from connection failures. Those were fixed together, built once and recaptured. The same reviewer scored all three resolved and returned `disposition: ship`. This verdict covers those scored fixes; unchanged imported settings/publication components were not independently re-audited.

Review screenshots and the synthetic fixture are local ignored artifacts under `.impeccable/review/`. User instructions are in [guided-workspace.md](guided-workspace.md).
