export async function validateCredentialFile(file) {
  if (!file || file.size > 65536)
    throw new Error("Select a service-account JSON file of at most 64 KiB.");
  const raw = await file.text();
  try {
    if (JSON.parse(raw).type !== "service_account") throw new Error();
  } catch {
    throw new Error(
      "Select a valid service-account JSON file downloaded from Google Cloud.",
    );
  }
  return raw;
}

export function modelConfigureRequest(provider, value) {
  if (provider !== "google_cloud")
    throw new Error("Only Google Cloud service accounts are supported.");
  return {
    path: "/api/settings/model/cloud",
    options: {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: value,
    },
  };
}

export function modelConnectionPresentation(data) {
  if (!data?.configured)
    return {
      label: "No connection",
      detail: "Configure a provider to enable AI repair.",
    };
  const label = data.test
    ? data.test.success
      ? "Connection tested"
      : "Connection test failed"
    : "Configured · not tested";
  const detail = `Google Cloud · ${data.connection.project} · global · ${data.model}`;
  return { label, detail };
}
