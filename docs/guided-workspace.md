# Using the tabbed workspace

Start `start_app.bat` in the managed APIShield worktree, then open http://127.0.0.1:8002. No APIShield account is needed. If the app is already running, refresh the browser to load the redesigned screens.

## Start with the example

1. Open **Help**, then choose **Try the free example**. This connects the supplied shipping project and compares its API contracts without an AI request.
2. Review the affected calls in Runs. Return to Workspace and choose **Try the example repair**.
3. After tests finish, open the repair. **Code changes** shows the proposed patch; **Tests & rules** shows the evidence. This example uses a supplied repair and real tests, without provider charges.

## Find the right screen

| Screen | What you do there |
| --- | --- |
| Workspace | Select a project and follow the next suggested action. More check options contains a source scan. |
| Runs | Review earlier checks, affected calls, proposed code, tests and optional GitHub drafts. |
| Settings → Project settings | Edit project/contracts, configure monitoring, define business rules or select a GitHub destination. |
| Settings → AI connection | Configure Google credentials and explicitly test the connection. |
| Help | Read the short guide and explanations, or start the free example. |

## Use your own project

Use **Settings → Appearance** to choose Light, Dark or System. Your choice is remembered in this browser.

Open a new run and choose **Impact graph** for the original-style node network. Select a red node to read its code and impact reason; downstream red nodes represent potential impact. Drag nodes, pan, zoom or Fit. Search keeps neighboring context; All code includes files/classes, and Affected isolates red paths. Small screens start in List. Close details with Escape. Supported relationships and coverage limitations are retained with each run; older runs do not gain new analysis automatically.

## Try the banking app

Open **Banking demo** from the sidebar, or visit `/banking`. Make a transfer with V1, switch the provider to V2, then try again to see the contract break. Choose **Analyze in APIShield** to connect the example, run **Check API changes**, and inspect its graph. **Try example repair** validates a supplied patch without AI charges. The banking screen's **Supplied V2 adapter** is a known fixture for demonstration; it does not apply a generated patch. All funds are simulated. See [banking walkthrough](../examples/banking/README.md).

Choose **Connect project** and provide a committed local Python repository, source/test directories, and old/new JSON OpenAPI contracts. Only committed source is checked; save your changes in Git first. Edit these choices under **Settings → Project settings → Project & contracts**.

In Workspace, choose **Check API changes**. The comparison makes no AI request. If supported calls are affected, configure Settings → AI connection and explicitly choose **Generate AI repair**. This sends selected code, contracts and confirmed requirements to the chosen provider, with provider charges. Tests run in a temporary copy.

A validated repair passed your configured tests and still requires review. Inspect Code changes and Tests & rules, then download the patch or prepare a GitHub draft preview. Creating the draft is a separate explicit action. APIShield does not apply patches to your original checkout or merge PRs.

Optional monitoring and business rules stay in Settings → Project settings. Tab switches preserve unsaved settings while the page remains open. Reloading the page does not preserve unsaved forms. Google credentials are held in server memory and must be selected again after a server restart.

Internal GitHub verification runs do not appear as separate repairs in ordinary history. Their evidence remains attached to the original proposal. If an action fails, dismissing its message does not retry it; use the action's explicit retry control. A failed patch load stays visible with **Reload patch**.

For details, see [AI setup](cloud-ai-setup.md), [GitHub drafts](github-drafts-setup.md), [monitoring](local-monitoring.md) and [business rules](requirements-workflow.md).
