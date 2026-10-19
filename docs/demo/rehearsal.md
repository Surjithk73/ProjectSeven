# CinemaFlow rehearsal evidence

This is a checklist and execution record, not a claim that the two-machine rehearsal has already happened.

- [ ] Invite `techASH5` to APIGuardTesting at the end of implementation; have the reviewer accept locally.
- [ ] Review and merge the initial movie-client setup PR; record its actual merge SHA.
- [ ] Start separate B providers and the initial client release; record B's actual IP and process health.
- [ ] Record one successful V1 booking with exact paise and seat identity.
- [ ] Switch only payment to V2; capture the client error and changed contract version.
- [ ] In manual mode, Check now, inspect impact and select Ask AI to Update. Retain the actual model response, proposed diff, generated checks and repository test results.
- [ ] Preview and publish the validated PR; record its actual URL/head SHA.
- [ ] Reviewer examines checks/diff, marks the draft ready if necessary, and merges it.
- [ ] Record exact merge SHA, main CI result, automatic deployment receipt, smoke result and running client SHA.
- [ ] Book successfully again; current impact highlights clear only after verified deployment.
- [ ] Repeat theatre V2 in automatic edit mode. Only the GitHub review/merge requires human action.
- [ ] Exercise both-provider changes, provider unavailability, a failed candidate, and failed deployment/rollback.

Local process/HTTP tests and mocked controller tests are useful implementation checks. They do not replace real Gemini generation, human review, LAN connectivity or deployment on the second Windows computer. Academic evaluation records remain separate and unchanged.
