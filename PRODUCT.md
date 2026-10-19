# APIShield
<!-- impeccable:product-schema 1 -->

## Platform
web

## Users
Developers maintaining Python REST integrations. The project owner wants to operate the application through a browser rather than CLI commands.

## Product Purpose
Identify documented API changes affecting application code and provide tested migration proposals for review.

## Operating Context
An existing React/Vite frontend and FastAPI service share a local commit-pinned Python engine. The user confirmed a complete local browser app, requested a UI/UX revamp and explicitly excluded authentication. No sign-in is required. Public hosting remains a later phase.

## Capabilities and Constraints
Direct requests/httpx GET/POST analysis, JSON OpenAPI comparison, trusted local Git repositories and configured independent tests. Developer-confirmed function-scoped business requirements link consuming operations to committed pytest checks; relevant checks gate repair acceptance and retain their own evidence. Disposable jobs retain evidence and patches without changing original source. Test validation is evidence, not universal correctness. Field-level/transitive intent analysis, controlled research evaluation, GitHub App publication, hosted scheduling and customer isolation remain later roadmap work.

## Brand Commitments
APIShield name; clear, candid developer language. No fabricated performance, customers, novelty or security claims.

## Evidence on Hand
Phase 1 payment demonstration, Phase 2 shipping example and a complete local browser workspace. The initial synthetic live assessment produced nine repairs that passed independent held-out checks; provider failures and missing-information behavior remain material limits. See [the assessment](docs/live-ai-quality-2026-10-12.md). These results do not establish general production repair quality.

## Product Principles
Keep original source unchanged. Show actionable findings before internal details. Distinguish tested repairs from failed or incomplete outcomes. Keep model and test evidence separate.
