# Google Cloud AI setup

Start `start_app.bat` in `C:/Users/surji/ProjectSeven` and open http://127.0.0.1:8002.

Settings → AI connection uses service-account JSON only. Choose a valid downloaded account file (at most 64 KiB, standard Google OAuth endpoint, no delegation). APIShield keeps a private managed copy outside the project and Git at `%USERPROFILE%/.apishield/credentials/service-account.json`. Windows access is restricted to the current user and SYSTEM. It loads automatically after restart; moving the original Downloads file does not break the connection.

Test connection makes one small paid request with `gemini-3.8-flash`. Configuration alone does not establish successful access. Remove connection deletes the managed copy and disables future requests; it does not revoke the account in Google Cloud. Existing jobs retain their captured credentials until completion or cancellation. Credentials never enter prompts, reports or repository subprocess environments.

All graph interpretation, intent inference and repair generation use this account. API-key entry and environment-key fallback are removed. Optional `APISHIELD_CREDENTIALS_FILE` in the launch environment selects another private path outside the project. CLI repair uses the managed account by default, or an explicit `--provider google_cloud --credentials C:/secure/service-account.json`.

See [current API workflow](current-api-ai-repair-walkthrough.md) for review, validation and Apply behavior. Generated tests reuse existing repository tests and add missing checks; repairs remain proposals until Apply is chosen.
