# NexusBank integration demo

Open `/banking` in the running APIShield app. It uses simulated USD balances and an in-memory provider; no external bank, credentials or real funds are involved.

1. Transfer with **V1 / Original adapter**.
2. Select **V2**. Transfer request nesting, balance response nesting and the refund endpoint change. Transfers fail without moving funds.
3. Choose **Analyze in APIShield**. The app connects a committed example snapshot. Run **Check API changes**, then open **Impact graph**.
4. Select a red node to inspect code and its dependency connections. **All code** includes files/classes; **Affected** isolates impacted paths. A propagated red node means potential impact, not a demonstrated failure.
5. Choose **Try example repair** to validate the supplied three-change patch with independent tests, or explicitly generate an AI repair after configuring a provider.
6. Back in the demo, **V2 / Supplied V2 adapter** demonstrates the known fixture fix. This switch does not install a generated patch. Transfer and refund again to check preserved integer cents.

Endpoints: accounts, account balance, transfers, transactions, refunds and beneficiaries. The source snapshot includes Python client/services/routes, named frontend API functions and tests. Static analysis does not fully resolve dynamic dispatch, arrow closures, complex TypeScript or runtime routing.

Reset clears only the demo's in-memory ledger. Original repository files and retained APIShield runs are not changed.
