# GitHub draft proposals

Start the local app with `./start_app.ps1` and open http://127.0.0.1:8002. No APIShield account is required. Install GitHub CLI and sign in using `gh auth login` yourself before using publication; APIShield uses that existing credential store and never offers a token field or starts login.

1. Choose **Connect project** in Workspace or Settings → Project settings to connect a local, committed Git repository and its current/updated JSON OpenAPI contracts. Tests use the application's Python environment for now.
2. In **Settings → Project settings → GitHub**, enter `owner/repository` and an existing base branch, then choose **Check and save target**. The signed-in GitHub account must have write access.
3. Generate a repair or use a validated retained offline repair. Open it in **Runs → GitHub draft** and choose **Prepare draft preview**. This checks the entire retained patch and reruns offline validation against the pinned source commit. It makes no GitHub writes and no model calls.
4. Review the changed files, complete patch, exact title/description, requirement checks and local test evidence. Choose **Create draft PR** explicitly to publish. The patch and JSON report downloads remain available independently of GitHub.
5. Use **Open draft PR** for review. Publication never merges, rebases, force-updates a branch, or modifies your source checkout. Repeated publication returns the same verified PR identity.

The remote base must equal the repair's pinned commit. If it differs or advances, create a fresh repair from the current base. Editing a target invalidates older previews. A prepared proposal uses its own preview revision, separately from the target revision.

If a remote response is lost, use **Check GitHub outcome** to reconcile the deterministic branch and PR. Reconciliation reads remote state; if it returns a ready proposal, review it and explicitly publish again to resume. A branch with conflicting content is left unchanged. Existing closed/merged matching PRs are reused rather than recreated. The displayed GitHub state is a retained observation, not continuous PR-status monitoring.

Interrupted local preparation is marked failed on restart and its reserved verification workspace is recovered. Interrupted publication requires reconciliation. Targets and proposals are stored in `~/.apishield/jobs/_publication`; retain this directory with the corresponding job evidence. Browser proposal selection is restored from local browser storage; CLI `report` can retrieve any retained proposal ID.

## CLI

Use the same application Python environment:

```powershell
python -m apishield proposal prepare JOB_ID --repository OWNER/REPOSITORY --base main
python -m apishield proposal report PROPOSAL_ID
python -m apishield proposal publish PROPOSAL_ID
python -m apishield proposal reconcile PROPOSAL_ID
```

Each command supports `--jobs-dir PATH`. Prepare prints the full reviewed proposal, including its exact PR body, and performs no publication. Publish is the separate write action. These commands share the browser's coordinator, storage and revision/evidence checks.

Only edits to allowed existing Python source files are publishable. Additions, deletions, renames, binary changes, mode changes, protected tests/configuration and modified validation evidence are rejected. Local tests execute trusted repository code; this is not an isolation boundary for malicious repositories.

GitHub CI is always labeled **not verified** by this workflow. Local validation and selected requirement checks do not prove complete semantic correctness. Other developers can advance the base after the final checkpoint; the draft retains its captured base and requires normal human review.
