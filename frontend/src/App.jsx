import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import NexusPay from "./pages/NexusPay";
import ApiShield from "./pages/ApiShield";
import Workspace from "./pages/Workspace";
import Banking from "./pages/Banking";
import "./theme.css";
export const API_URL = "";
function Demo({ provider = false }) {
  const [state, setState] = useState(null),
    [error, setError] = useState("");
  useEffect(() => {
    let disposed = false;
    async function refresh() {
      try {
        const response = await fetch(`${API_URL}/api/state`);
        if (!response.ok) throw new Error("Demo API unavailable");
        const data = await response.json();
        if (!disposed) {
          setState(data);
          setError("");
        }
      } catch (e) {
        if (!disposed) setError(e.message);
      }
    }
    refresh();
    const timer = setInterval(refresh, 1500);
    return () => {
      disposed = true;
      clearInterval(timer);
    };
  }, []);
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <nav className="flex flex-wrap gap-6 border-b border-gray-200 bg-white p-4">
        <Link to="/">Back to workspace</Link>
        <Link to="/demo">Payment repair demo</Link>
        <Link to="/provider">NexusPay provider</Link>
      </nav>
      <main className="max-w-7xl mx-auto p-6">
        {error && (
          <p role="alert">
            {error}. Start the provider for the full payment demonstration.
          </p>
        )}
        {state ? (
          provider ? (
            <NexusPay systemState={state} />
          ) : (
            <ApiShield systemState={state} />
          )
        ) : (
          <p role="status">Loading demo…</p>
        )}
      </main>
    </div>
  );
}
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Workspace />} />
        <Route path="/banking" element={<Banking />} />
        <Route path="/demo" element={<Demo />} />
        <Route path="/agent" element={<Demo />} />
        <Route path="/provider" element={<Demo provider />} />
        <Route
          path="*"
          element={
            <div className="p-8">
              Page not found. <Link to="/">Return to workspace</Link>
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
