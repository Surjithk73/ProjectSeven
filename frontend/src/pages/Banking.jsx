import { useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, ArrowRightLeft, Check, CircleAlert, Code2, Landmark, RefreshCw, RotateCcw, Server, ShieldCheck, Wallet } from "lucide-react";
import { requestJSON } from "../workspace";
import { accountOverview, sendMoney, reverseTransfer } from "../../../examples/banking/frontend/api";
import ThemeControl from "../components/ThemeControl";
import "../workbench.css";
import "./banking.css";

const post = body => ({ method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
const money = cents => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(cents / 100);
const accountName = id => id === "checking" ? "Everyday account" : "Savings";
function amountInCents(amount) {
  if (!/^\d+(\.\d{1,2})?$/.test(amount)) throw new Error("Enter a positive amount with at most two decimal places.");
  const [whole, decimal = ""] = amount.split(".");
  const value = Number(whole) * 100 + Number(decimal.padEnd(2, "0"));
  if (!Number.isSafeInteger(value) || value <= 0 || value > 100000000) throw new Error("Choose an amount between $0.01 and $1,000,000.");
  return value;
}
async function checked(response) {
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || "Bank request failed. Try again.");
  return body;
}
export default function Banking() {
  const [tab, setTab] = useState("client");
  const [state, setState] = useState(null);
  const [contract, setContract] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [amount, setAmount] = useState("25.00");
  const [source, setSource] = useState("checking");
  const [destination, setDestination] = useState("savings");
  const [message, setMessage] = useState("");
  const [balanceError, setBalanceError] = useState("");
  const [clientAccounts, setClientAccounts] = useState(null);

  async function refreshClient() {
    try {
      const data = await accountOverview().then(checked);
      setClientAccounts(data.accounts); setBalanceError("");
    } catch (e) { setClientAccounts(null); setBalanceError(e.message); }
  }
  async function refresh() {
    const [data, docs] = await Promise.all([requestJSON("/api/banking/state"), requestJSON("/api/banking/openapi")]);
    setState(data); setContract(docs); await refreshClient();
  }
  useEffect(() => {
    let live = true;
    // Resolve the working adapter before checking the client API on first load.
    requestJSON("/api/banking/state").then(async data => {
      const [docs, client] = await Promise.all([requestJSON("/api/banking/openapi"), accountOverview().then(checked).then(data => ({ data }), e => ({ error: e.message }))]);
      if (!live) return;
      setState(data); setContract(docs); setClientAccounts(client.data?.accounts || null); setBalanceError(client.error || "");
    }).catch(e => { if (live) setError(e.message); });
    return () => { live = false; };
  }, []);
  async function action(fn, success = "") {
    setBusy(true); setError(""); setMessage("");
    try { await fn(); await refresh(); setMessage(success); }
    catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  async function connect() {
    await requestJSON("/api/examples/banking", post({}));
    window.location.href = "/?project=banking-example";
  }
  function changeTab(next) { setTab(next); setMessage(""); setError(""); }
  const operations = Object.entries(contract?.paths || {}).flatMap(([path, item]) =>
    Object.entries(item).filter(([method]) => ["get", "post", "put", "patch", "delete"].includes(method)).map(([method, details]) => ({ method, path, details })));

  return <main className="guided-shell banking-shell nexus-bank">
    <div hidden><ThemeControl /></div>
    <header className="bank-topbar">
      <a className="bank-brand" href="/banking"><span className="bank-brand-mark"><Landmark size={23} /></span>NexusBank</a>
      <span className="bank-simulation"><ShieldCheck size={16} />Simulated funds · local demo</span>
      <a className="bank-workspace" href="/"><ArrowLeft size={16} />APIShield workspace</a>
    </header>
    <div className="bank-workspace-body">
      <div className="bank-page-heading">
        <div><h1>Your banking workspace</h1><p>Everyday banking, connected to a versioned API.</p></div>
        <button className="primary-button" disabled={busy || !state} onClick={() => action(connect)}>Open in APIShield<ArrowRight size={17} /></button>
      </div>
      <div className="bank-navigation">
        <div className="bank-tabs" role="tablist" aria-label="Banking workspace" onKeyDown={e => {
          if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(e.key)) {
            e.preventDefault();
            const next = e.key === "Home" ? "client" : e.key === "End" ? "provider" : tab === "client" ? "provider" : "client";
            changeTab(next); document.getElementById(`bank-tab-${next}`).focus();
          }
        }}>
          {[["client", Wallet, "Client application"], ["provider", Server, "API provider"]].map(([key, Icon, label]) => <button key={key} id={`bank-tab-${key}`} role="tab" aria-selected={tab === key} aria-controls={`bank-panel-${key}`} tabIndex={tab === key ? 0 : -1} onClick={() => changeTab(key)}><Icon size={18} />{label}</button>)}
        </div>
        <span className="bank-version">Provider<strong>{state ? state.version.toUpperCase() : "Loading…"}</strong></span>
      </div>
      {error && <div className="bank-notice bank-notice-error" role="alert"><CircleAlert size={19} /><div><strong>Action couldn’t be completed</strong><p>{error}</p></div><button className="text-button" disabled={busy} onClick={() => action(refresh)}>Refresh</button></div>}
      {message && <div className="bank-notice bank-notice-success" role="status"><Check size={18} />{message}</div>}
      {!state && !error && <div className="bank-loading" role="status">Loading your banking workspace…</div>}
      <section id="bank-panel-client" role="tabpanel" aria-labelledby="bank-tab-client" hidden={tab !== "client"} className="bank-panel">
        <div className="bank-section-heading"><div><h2>Accounts</h2><p>Your balances in USD</p></div><button className="secondary-button" disabled={busy || !state} onClick={() => action(refresh)}><RefreshCw size={15} className={busy ? "bank-refreshing" : ""} />Refresh balances</button></div>
        {balanceError && <div className="bank-notice bank-notice-error" role="alert"><CircleAlert size={19} /><div><strong>The client can’t read the active API</strong><p>{balanceError}. Open APIShield to check for changes and review an AI repair.</p></div></div>}
        <div className="bank-account-grid">{(state?.accounts || [{ id: "checking", name: "Everyday account" }, { id: "savings", name: "Savings" }]).map((account, index) => {
          const balance = clientAccounts?.find(a => a.id === account.id)?.balance_cents;
          return <article className={`bank-account bank-account-${index}`} key={account.id}>
            <div className="bank-account-label"><span>{account.name}</span><Wallet size={22} /></div><strong>{balance == null ? "—" : money(balance)}</strong>
            <div className="bank-account-footer"><span>{balanceError ? "Balance unavailable" : "Available balance"}</span><code>{account.id.toUpperCase()}</code></div>
          </article>;
        })}</div>
        <div className="bank-client-grid">
          <section className="bank-transfer">
            <div className="bank-section-heading"><div><h2>Move money</h2><p>Transfer between your accounts.</p></div><ArrowRightLeft size={21} /></div>
            <form onSubmit={e => { e.preventDefault(); action(() => sendMoney(source, destination, amountInCents(amount)).then(checked), "Transfer completed. Your balances are up to date."); }}>
              <fieldset disabled={busy || !state}>
                <label>From<select value={source} onChange={e => { setSource(e.target.value); if (e.target.value === destination) setDestination(source); }}><option value="checking">Everyday account</option><option value="savings">Savings</option></select></label>
                <label>To<select value={destination} onChange={e => { setDestination(e.target.value); if (e.target.value === source) setSource(destination); }}><option value="savings">Savings</option><option value="checking">Everyday account</option></select></label>
                <label>Amount<div className="bank-amount"><span>$</span><input aria-label="Amount in USD" inputMode="decimal" value={amount} onChange={e => setAmount(e.target.value)} required /><span>USD</span></div></label>
                <button className="primary-button" type="submit">{busy ? "Processing…" : "Transfer money"}<ArrowRight size={17} /></button>
              </fieldset>
            </form>
            <p className="bank-form-note"><ShieldCheck size={15} />Local transfers. No real money moves.</p>
          </section>
          <section className="bank-transactions">
            <div className="bank-section-heading"><div><h2>Recent transactions</h2><p>Transfers and their refund status.</p></div><span className="bank-count">{state?.transactions.length || 0}</span></div>
            {state?.transactions.length ? <ul className="bank-transaction-list">{[...state.transactions].reverse().map(t => <li key={t.id}>
              <span className="bank-transfer-icon"><ArrowRightLeft size={19} /></span>
              <div className="bank-transaction-description"><strong>{accountName(t.source)}<ArrowRight size={13} />{accountName(t.destination)}</strong><code>{t.id}</code></div>
              <div className="bank-transaction-amount"><strong>{money(t.amount_cents)}</strong>{t.refunded ? <span className="bank-refunded"><Check size={12} />Refunded</span> : <button className="text-button" disabled={busy} onClick={() => action(() => reverseTransfer(t.id).then(checked), "Refund completed. Funds returned to the original account.")}>Refund</button>}</div>
            </li>)}</ul> : <div className="bank-empty"><ArrowRightLeft size={30} /><h3>Your transfers will appear here</h3><p>Move money between your accounts to get started. You can refund a completed transfer from this list.</p></div>}
          </section>
        </div>
      </section>
      <section id="bank-panel-provider" role="tabpanel" aria-labelledby="bank-tab-provider" hidden={tab !== "provider"} className="bank-panel">
        <div className="bank-provider-grid">
          <section className="bank-provider-settings">
            <div className="bank-section-heading"><div><h2>Provider version</h2><p>Choose which API the client connects to.</p></div><Server size={22} /></div>
            <fieldset className="bank-version-options" disabled={busy || !state}>
              <legend className="sr-only">Active provider version</legend>
              {[["v1", "Original API", "The original request and response formats."], ["v2", "Updated API", "Changes balance, transfer and refund contracts."]].map(([version, title, description]) => <label key={version}>
                <input type="radio" name="provider-version" value={version} checked={state?.version === version} onChange={() => action(() => requestJSON("/api/banking/controls", post({ version, adapter: "original" })), `${version.toUpperCase()} is now active. The client code has not been changed.`)} />
                <span><strong>{version.toUpperCase()} · {title}</strong><span>{description}</span></span>
              </label>)}
            </fieldset>
            <div className="bank-provider-status"><ShieldCheck size={20} /><div><strong>{state?.repaired ? "AI repair applied" : "Original client code"}</strong><p>{state?.repaired ? "The demo runs your applied working files." : "Switching the provider leaves client code unchanged."}</p></div></div>
            <button className="secondary-button" disabled={busy || !state} onClick={() => action(() => requestJSON("/api/banking/reset", post({})), "Demo reset to V1. Original client code and starting balances restored.")}><RotateCcw size={16} />Reset demo to V1</button>
            <p className="bank-reset-note">Restores the demo client code, starting balances and empty transaction history.</p>
          </section>
          <section className="bank-endpoints">
            <div className="bank-section-heading"><div><h2>Active API contract</h2><p>{contract?.info?.title || "Loading documentation…"}</p></div><span className="bank-count">{operations.length} endpoints</span></div>
            <ul>{operations.map(({ method, path, details }) => <li key={`${method}:${path}`}><span className={`bank-method bank-method-${method}`}>{method.toUpperCase()}</span><div><code>{path}</code>{details.summary && <p>{details.summary}</p>}</div></li>)}</ul>
            <a href="/api/banking/openapi" target="_blank" rel="noreferrer"><Code2 size={16} />Open API documentation<ArrowRight size={15} /></a>
          </section>
        </div>
        <section className="bank-migration-guide"><h2>Try the migration workflow</h2><ol><li>Activate V2, then try a transfer in the client tab.</li><li>Open APIShield and select <strong>Check for API Changes</strong>.</li><li>Request an AI repair, review the patch and test evidence, then apply it.</li><li>Return here and refresh balances to try the repaired client.</li></ol></section>
      </section>
      <footer className="bank-footer"><span><Landmark size={15} />NexusBank demo</span><span>Powered by the current client working files</span></footer>
    </div>
  </main>;
}
