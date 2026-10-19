from github import Github, GithubException
from config import get_setting
import datetime

try:
    from fastmcp import FastMCP
    mcp = FastMCP("GitHub Editor")
except ImportError:
    class _NoOpMCP:
        def tool(self):
            return lambda fn: fn
    mcp = _NoOpMCP()

def apply_github_patch(file_path: str, patch_code: str, original_intent: str, ips_score: int | None = None) -> dict:
    """
    Creates a new branch, commits the patch_code to the specified file_path, and opens a Pull Request.
    """
    token = get_setting('GITHUB_TOKEN')
    repo_name = get_setting('GITHUB_REPO')
    
    if not token or not repo_name:
        return {"status": "error", "message": "GITHUB_TOKEN or GITHUB_REPO is not configured"}
        
    # In our local repo, the client code is in client_app/.
    # In the GitHub repo (clientappP7), it is at the root.
    repo_relative_path = file_path.replace("\\", "/")
    if repo_relative_path.startswith("client_app/"):
        repo_relative_path = repo_relative_path[len("client_app/"):]
    elif "ProjectSeven" in repo_relative_path:
        repo_relative_path = repo_relative_path.split("ProjectSeven")[-1].lstrip("/")
        if repo_relative_path.startswith("client_app/"):
            repo_relative_path = repo_relative_path[len("client_app/"):]
        
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        # 1. Get default branch (main)
        default_branch = repo.default_branch
        ref = repo.get_git_ref(f"heads/{default_branch}")
        
        # 2. Create new branch
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"codex/apishield-fix-{timestamp}"
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=ref.object.sha)
        
        # 3. Get the file to update
        contents = repo.get_contents(repo_relative_path, ref=default_branch)
        
        # 4. Update the file in the new branch
        commit_message = f"APIShield Auto-Patch: Fix for {repo_relative_path}"
        repo.update_file(
            contents.path,
            commit_message,
            patch_code,
            contents.sha,
            branch=branch_name
        )
        
        # 5. Open Pull Request
        pr_title = f"[APIShield] Auto-fix for intent '{original_intent}'"
        ips_evidence = f'{ips_score}/100' if type(ips_score) is int and 0 <= ips_score <= 100 else 'unavailable'
        pr_body = f"""## APIShield Auto-Patch

**Breaking Change Detected** in upstream API schema.
**Impacted File:** `{repo_relative_path}`
**Intent:** {original_intent}

**Validation:**
- Intent Preservation Score: {ips_evidence}
- CI: Pending

*Opened automatically by APIShield autonomous agent.*
"""
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=branch_name,
            base=default_branch,
            draft=True
        )
        
        return {
            "status": "success",
            "pr_url": pr.html_url,
            "pr_number": pr.number,
            "branch_name": branch_name
        }
    except GithubException as e:
        return {"status": "error", "message": f"GitHub API error: {e.data}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_pr_status(pr_number: int) -> dict:
    """
    Checks the CI status and mergeability of a PR.
    """
    token = get_setting('GITHUB_TOKEN')
    repo_name = get_setting('GITHUB_REPO')
    
    if not token or not repo_name:
        return {"status": "error", "message": "GITHUB_TOKEN or GITHUB_REPO is not configured"}
        
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        # Get checks
        last_commit = repo.get_commit(pr.head.sha)
        check_runs = last_commit.get_check_runs()
        
        checks = []
        all_passed = True
        any_pending = False
        
        for run in check_runs:
            checks.append({
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion
            })
            if run.status != "completed":
                any_pending = True
                all_passed = False
            elif run.conclusion != "success":
                all_passed = False
                
        # An empty check list supplies no passing evidence.
        if not checks:
            all_passed = False
            
        return {
            "status": "success",
            "mergeable": pr.mergeable,
            "state": pr.state,
            "checks": checks,
            "all_checks_passed": all_passed,
            "any_pending": any_pending,
            "ci_evidence": "available" if checks else "unavailable"
        }
    except Exception as e:
         return {"status": "error", "message": str(e)}

def merge_pr(pr_number: int) -> dict:
    """
    Merges the PR.
    """
    token = get_setting('GITHUB_TOKEN')
    repo_name = get_setting('GITHUB_REPO')

    if not token or not repo_name:
        return {"status": "error", "message": "GITHUB_TOKEN or GITHUB_REPO is not configured"}
    
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        if pr.mergeable:
            status = pr.merge()
            return {"status": "success", "merged": status.merged, "message": status.message}
        else:
            return {"status": "error", "message": "PR is not mergeable"}
    except Exception as e:
         return {"status": "error", "message": str(e)}

# Keep locally called functions callable even if registration returns a Tool.
for _tool_function in (apply_github_patch, get_pr_status, merge_pr):
    mcp.tool()(_tool_function)

if __name__ == "__main__":
    mcp.run()
