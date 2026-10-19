# Local browser workflow

User instruction: complete and test the app frontend so it can be used as a real user, using Superpowers, Impeccable and Ponytail. Success: no CLI required for trying the shipping workflow, registering a trusted local integration, checking API changes or reviewing/downloading a tested patch.

## Scope and approach
Extend the existing React/FastAPI application with a default integration workspace. Reuse Phase 2 jobs and existing dependencies. Preserve the payment demonstration under separate routes. Compared with merely exposing raw jobs, browser onboarding makes this usable; building hosting/accounts now adds independent infrastructure outside the verified local foundation. A local delivery is the working assumption while the scope question is pending.

## Workflow
Empty state offers a one-click shipping example or an integration form. The form accepts a name, local Git root, relative source directories, pytest directory and two JSON OpenAPI uploads. It explains commit-only source and trusted host execution; browser requests never supply arbitrary shell commands. Registration persists outside source; editing publishes immutable validated configuration versions without changing past evidence. Users select an integration, scan, compare or request a model repair. Shipping additionally offers an explicitly labeled offline example repair. Settings accepts a model key into server memory only, never returning it in successful or invalid responses. No key is saved to disk.

Jobs show honest queued/running/terminal states, persistent history and cancellation. Selected reports show affected calls, coverage limitations, changed operations, attempts, test output, commit and hashes. Validated patches can be previewed and downloaded; failed jobs never expose patch actions. Raw JSON is downloadable for reproducibility. Model availability is visible and missing credentials have a clear recovery instruction.

## Local boundaries
Onboarding is a local administration operation: deny non-loopback clients and unexpected browser Origin/Host values. Fixed pytest argv only; strict schemas and source path validation; reject an integration repository containing the job/config root. Persist an atomic local registry, merge server allowlist without allowing browser overrides. Only the server-created shipping example can choose a server-known offline candidate. No browser-supplied candidate paths. Existing configured CLI/service interfaces remain compatible.

## Visual and interaction direction
Operate mode; inherit the existing white/slate/purple visual system. A restrained navigation rail, integration selector and action toolbar lead into readable findings and run history. Use existing lucide icons and CSS/native forms; no new component framework. Responsive single-column mobile layout, visible focus, reduced-motion support, loading/error/empty states, labeled uploads and status text. No invented analytics or decorative graph needed to use the app.

## Verification
Backend acceptance tests cover registration persistence, strict requests, local-origin boundary, real offline shipping repair and artifact access. Frontend checks cover response failure handling, status/evidence presentation; browser exercises onboarding and real scan/compare/repair, patch view/download, history, failures and desktop/mobile layout. Run full Python suite, frontend tests/build/lint and independent correctness/design reviews.
