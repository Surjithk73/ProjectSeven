import { useEffect, useState } from "react";
import { Sun, Moon, Monitor } from "lucide-react";
import { themePreference, resolvedTheme } from "../workbench";

export default function ThemeControl() {
  const [preference, setPreference] = useState(() => {
    try {
      return themePreference(localStorage.getItem("apishield-theme"));
    } catch {
      return "system";
    }
  });
  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const apply = () => {
      document.documentElement.dataset.workspaceTheme = resolvedTheme(
        preference,
        media.matches,
      );
    };
    apply();
    media.addEventListener("change", apply);
    try {
      localStorage.setItem("apishield-theme", preference);
    } catch {
      /* Storage is optional. */
    }
    return () => media.removeEventListener("change", apply);
  }, [preference]);
  const Icon =
    preference === "system" ? Monitor : preference === "dark" ? Moon : Sun;
  return (
    <label className="theme-control">
      <Icon size={17} aria-hidden="true" />
      <span className="sr-only">Appearance</span>
      <select
        aria-label="Appearance"
        value={preference}
        onChange={(event) => setPreference(event.target.value)}
      >
        <option value="light">Light</option>
        <option value="dark">Dark</option>
        <option value="system">System</option>
      </select>
    </label>
  );
}
