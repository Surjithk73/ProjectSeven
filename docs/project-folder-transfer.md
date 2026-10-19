# Project folder transfer

The latest app source now lives at `C:/Users/surji/ProjectSeven`.

The older source and Git data were preserved at `.project-backups/original-2026-10-14/` before updating the root. Its 954 copied files were verified byte-for-byte with SHA-256. Python/Node dependency directories and caches were excluded from that backup; saved dependency files allow them to be recreated. The original local `.env` remains in the root and is also preserved privately in the ignored backup.

The root Git metadata and its existing main branch were retained. The linked `codex/phase1-foundation` worktree and its files remain available; the new code is also present in the primary checkout as local changes. No Git reset, commit, push, branch replacement or backup deletion was performed. `.project-backups/` is ignored to avoid accidentally adding old source, Git data or credentials to the active repository.

Latest source transfer verification matched 273 code/document/config files; generated dependencies, artifacts, logs and the deliberately extended `.gitignore` were excluded from that comparison. From the original folder, all 56 frontend tests, 18 targeted backend tests and the production build passed. Frontend dependencies were installed from the copied lockfile. The editable Python package registration is moved to the original folder so the CLI uses that source too.

Start the app from the project root with `./start_app.ps1 -NoBrowser` or `start_app.bat`. The local URL remains `http://127.0.0.1:8002/`. Job history and registered integrations retain their existing local storage; the transfer does not erase them.
