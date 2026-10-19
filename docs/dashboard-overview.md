# Dashboard overview details

The integration snapshot uses retained source/contract evidence: accepted API version, distinct consuming method/path pairs, distinct consumer source files, and the latest API comparison timestamp. Missing evidence remains explicitly unrecorded rather than becoming invented counts. The most recent comparison determines Monitoring status. Successful means that comparison completed, not that the application has no breaking changes; its actual outcome appears directly underneath. Failed, cancelled, running, and unrecorded checks remain distinct.

Recent activity includes endpoint discovery counts, changed-operation counts, validation readiness, and applied-file counts from the recorded run. Existing status badges and links to full evidence remain available.

Automatic checks on the overview is explicitly a UI preview, as requested. Its toggle and 15-minute/hourly/6-hour/daily choices are saved only in browser localStorage under a per-integration `apishield-check-preview:` key. It performs no fetch, scheduling, background monitoring, provider switch, repair generation, or automatic Apply. Existing real monitoring settings are not modified by the preview. The earlier saved UI's Auto-Heal control was inspected as a reference; its backend behavior was not reactivated.

Verification: 75 frontend tests and the production build passed. Four new tests cover snapshot provenance, status truthfulness, outcome details, and isolated/validated preview storage. Lint has six existing warnings; the mechanical design detector found no issues in the changed UI targets. Rendered browser verification remains unavailable under the earlier browser restriction. No backend or academic experiment records were changed.
