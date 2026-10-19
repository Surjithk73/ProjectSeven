# GitHub draft preview without an account

Prepare draft preview first constructs a local draft from the selected validated repair and its retained patch. It does not require GitHub authentication, a remote repository, or a configured publication target. The visible title uses the project display name; the description includes changed files, affected API operations, recorded validation and source provenance. Patch contents are the real retained diff, never an invented example.

The local preview is labelled Not published and offers Download draft (Markdown plus the patch) and Connect GitHub to continue, which opens the project's existing GitHub settings. A configured target continues through the existing backend preparation/revalidation flow. Creating a remote draft PR still requires an explicit Create draft PR action; the publication service and its revision, provenance, remote-effect and reconciliation guards are unchanged. Preview generation does not call an LLM or write working-source files.

If GitHub target lookup or connected preparation fails, the already-generated local preview remains visible. Optional browser storage failures no longer hide an otherwise successful proposal response. Local preview content itself is component state, not an automatically persisted copy of repository source.

Verification: 77 frontend tests and the production build passed; lint retains six existing warnings. New tests verify actual diff/file/provenance retention without a GitHub target and rejection of unvalidated or missing-patch evidence. The design detector found no issues. No real GitHub branch, commit or pull request was created during verification. Rendered browser verification remains unavailable under the earlier browser restriction.
