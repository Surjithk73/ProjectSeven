# Community graph and compact comparison

The Overview now browses all retained API endpoints through a short rail. Original and Updated versions are visible together on desktop. Request, Responses, Full details and Shared schemas switch both panes together. Schema panes scroll internally. Narrow screens use a horizontal endpoint rail and stacked version panes.

The Impact graph opens with detected communities, colored consistently within each community. Open a community to browse its supported code, endpoints, tests and declared intents. A sparse spanning forest reduces the default lines without deleting evidence. Select a node to see its actual incident links and retained source. Red outlines preserve recorded impact status; community impact means at least one member is affected.

Generate AI graph explicitly sends redacted retained node names, file paths and up to 800 characters of code per node to the configured Gemini connection. It makes one bounded model request (60 seconds, 4096 output tokens), supporting at most 120 nodes and 128 KiB of context. Charges depend on the configured provider. No background AI generation or retry. AI assigns existing node indices to business-flow communities; every node must be assigned exactly once. Optional inferred relationships are separately labeled, hidden until requested, and never influence impact analysis or repair validation. Persisted overlays are revalidated and tied to the base graph hash.

This is inspired by Graphify's extraction/inference distinction and community coloring, not an installation of Graphify or a claim of its language/media coverage. The base graph remains the existing Python AST and bounded JavaScript source analysis; unsupported/dynamic calls remain subject to existing coverage limitations.

Validation: frontend tests, production build, lint; Python overlay and dashboard API tests, retained contract, repository graph, banking/browser setup tests. Automated graph-generation API tests mock the provider and verify failure recovery and retained evidence integrity. During the first unisolated test, inherited credentials caused a failed live request; tests now explicitly disable ambient credentials. No successful live AI overlay is claimed. Fresh desktop/mobile capture is pending because browser policy rejected access; numerical layout/source checks are not visual approval.

## Current validation (2026-10-14)
- Frontend: 51 tests passed; production bundle built. Lint has six incumbent warnings, none in the new components/helpers.
- Backend: 14 graph/dashboard tests and 27 contract/repository/banking/browser tests passed (41 total).
- Fresh code review: no Critical or Important findings in this feature's scope.
- File-only design detector: one incumbent active-tab underline false positive. No new primary design finding.
- Finish review disposition: recapture. Fresh desktop/mobile/648px target captures are unavailable under the current browser access restriction. Source and numerical tests do not approve visual fidelity.
- Managed local app restarted idle on port 8002. Retained banking report: 48 recorded nodes, 72 recorded edges, five detected communities, six original and six updated endpoints. New graph AI route is registered; connection is configured but has no successful graph interpretation/test result.

## Motion, diff highlights and settled layout refinement

User-approved paired Overview/community composition is retained. Added and removed endpoint selections receive subtle theme-aware green/red fills; aligned JSON lines show actual additions/removals with plus/minus markers. Unchanged lines remain neutral, including punctuation-only trailing commas. Alignment is bounded to 400,000 comparison cells; larger sections use unchanged prefix/suffix with a coarser changed middle, rather than unbounded work. Paired panes use one 240ms clipped reveal on endpoint/detail selection, with immediate control feedback; reduced motion disables animations/transitions.

Graph layout now seeds a golden-angle spiral, uses stronger D3 links and weaker centering rather than fixed grid anchors, settles before display, and resolves node-label rectangles. This follows the approach observed in Graphify's exporter (spiral seed, physics stabilization, then freeze), adapted to the existing D3 renderer without adding another graph dependency. Source reference: https://github.com/Graphify-Labs/graphify/blob/v8/graphify/exporters/html.py . Community fit caps scale at 0.85; detailed code fit caps at 1.1, both center content and preserve node dragging independently of camera movement.

Validation: 54 frontend tests passed, including bounded camera sizing, adjacent branch proximity, dense label non-overlap and true added/removed line highlights. Production build and lint checked after changes. Backend behavior and AI calls are unchanged. Current user screenshots establish the incumbent, not fresh proof of this refinement; browser capture remains denied and final visual verification remains pending.

Final refinement checks: 56 frontend tests passed; production build passed; lint has only six incumbent warnings. Code reviewer scored both material fixes resolved: community/label geometry now includes status/wrapping space, and graphs above 160 nodes use a relationship-ordered separated grid with no physics, while list mode skips layout. The independent 1,000-node layout check took approximately 2.83 ms on this host. This is source/numerical evidence, not a visual verdict. Finish disposition remains recapture.

## Readability correction from user screenshot

The user's 2026-10-14 screenshot exposed pale, undersized evidence and weak selected controls. The existing paired composition is preserved with dark light-theme primary text #101c2e, secondary #35445b, stronger boundaries #c6d1df, inset #eaf0f7 and accent #144dcb. Body is 17px/500, detail controls16px/650, JSON evidence15px/550, version headers19px/750 and version identifiers14px/700. Global compact metadata is15/16px. Dark-theme text remains light (#f1f5fc primary, #c4d0e3 secondary) for contrast. Change colors darken to green#195337 and red#8f1f36 while keeping existing subtle fills.

Endpoint rail is256px atdesktop and210px atmedium, with tighterrowpadding; paths receive native word-break opportunities at slash boundaries. Active detail tabs use solidaccent fills. Code panes retain bounded internal scrolling and now provide340px desktopheight with larger code. Original/Updated boundaries are stronger; factual content, graph evidence, AI/provider behavior, and source files are unchanged.

Fresh production build passed; lint has only six incumbent warnings. File-only detector remains the known active-tab-underline falsepositive. Palette-only contrast calculations (not computed-browser verification): primary white17.11:1, secondary inset8.6:1, active tab7.11:1, added8.22:1, removed7.86:1, dark text13.94:1. New bundle index-iVMRflZE.js is served atlocalhost8002. No new behavior tests added for this reversible styling correction. Finish reviewer disposition is recapture because source/palette checks and the incumbent user screenshot do not prove the new desktop/mobile render.

## Test and technical section redesign

Tests & rules now uses a two-column validation workspace: test executions on the left, compact business rules on the right. The neutral empty state states that repair tests have not run; recorded command statuses still honor timeout/cancellation before exit-code success. Attempt number, duration, stdout/stderr and capped-output notes remain accessible. Rule outcomes reuse the existing evidence-guarded presentation; declared rules never become passed merely through styling. Source/rule/test relationships remain a native disclosure.

Technical details uses separate coverage and provenance columns. Real coverage notes receive amber treatment, source file details remain visible and full raw contract diff remains expandable. A compact striped run-record table retains full run ID, commit, original/updated API and business-rule fingerprints with wrapping. JSON report download still invokes the original action. A short explanation makes fingerprint purpose explicit. Both layouts stack at1000px, with label/value rows stacking at600px. The established Source Sans3, theme colors and reading hierarchy remain intact.

Validation: 56 existing frontend tests passed, production build passed, lint contains only six incumbent warnings. File-only detector reports only the known active-tab underline falsepositive. The user's screenshots show the incumbent, not the new render; fresh visual verification remains pending under browser access restrictions. No backend behavior, source mutations or AI calls added.
