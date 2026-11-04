"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import Icon from "@/components/Icon";
import { Protected, useToast } from "@/components/Providers";
import { Field } from "@/components/ui";
import { api } from "@/lib/api";

function ChangePassword() {
  const toast = useToast();
  const router = useRouter();
  const [v, setV] = useState({ current_password: "", new_password: "", confirm: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k, val) => setV((s) => ({ ...s, [k]: val }));

  async function submit(e) {
    e.preventDefault();
    if (v.new_password !== v.confirm) return setError("The new passwords don't match.");
    setBusy(true);
    setError("");
    try {
      await api("/password", { method: "POST", body: v });
      toast("Password changed.");
      router.push("/dashboard");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="auth fade-up">
      <div className="auth-head"><Icon name="key" size={36} /><h1 style={{ marginTop: 10 }}>Change password</h1></div>
      <form className="glass auth-card" onSubmit={submit}>
        {error && <div className="form-error" role="alert">{error}</div>}
        <Field label="Current password" name="current_password" type="password" required autoComplete="current-password" value={v.current_password} onChange={set} />
        <Field label="New password" name="new_password" type="password" required autoComplete="new-password" value={v.new_password} onChange={set}
          hint="At least 8 characters, with letters and numbers." />
        <Field label="Confirm new password" name="confirm" type="password" required autoComplete="new-password" value={v.confirm} onChange={set} />
        <button className="btn lg block" disabled={busy}>{busy ? "Updating…" : "Update password"}</button>
      </form>
    </div>
  );
}

export default function PasswordPage() {
  return <Protected level="login"><ChangePassword /></Protected>;
}
