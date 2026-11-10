"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { KvLogo } from "@/components/Brand";
import Icon from "@/components/Icon";
import { PageSkeleton } from "@/components/Providers";
import { Field } from "@/components/ui";
import { api } from "@/lib/api";

function ResetForm() {
  const token = useSearchParams().get("token") || "";
  const [link, setLink] = useState({ loading: true });
  const [v, setV] = useState({ new_password: "", confirm: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const set = (k, val) => setV((s) => ({ ...s, [k]: val }));

  useEffect(() => {
    api(`/auth/reset-password?token=${encodeURIComponent(token)}`)
      .then((d) => setLink({ name: d.name }))
      .catch((e) => setLink({ error: e.message }));
  }, [token]);

  async function submit(e) {
    e.preventDefault();
    if (v.new_password !== v.confirm) return setError("The two passwords don't match.");
    setBusy(true);
    setError("");
    try {
      await api("/auth/reset-password", { method: "POST", body: { token, new_password: v.new_password } });
      setDone(true);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  if (link.loading) return <PageSkeleton />;

  if (link.error || done) {
    return (
      <div className="auth glass state-card fade-up">
        <div className="big"><Icon name={done ? "check" : "key"} size={34} /></div>
        <h1>{done ? "Password changed" : "Link not valid"}</h1>
        <p className="muted">{done ? "You can now sign in with your new password." : link.error}</p>
        <Link className="btn" href="/login">Go to sign in</Link>
      </div>
    );
  }

  return (
    <div className="auth fade-up">
      <div className="auth-head">
        <KvLogo height={72} />
        <h1>Choose a new password</h1>
        <p>Hi {link.name}, set a new password for your alumni account.</p>
      </div>
      <form className="glass auth-card" onSubmit={submit}>
        {error && <div className="form-error" role="alert">{error}</div>}
        <Field label="New password" name="new_password" type="password" required autoFocus autoComplete="new-password"
          value={v.new_password} onChange={set} hint="At least 8 characters, with letters and numbers." />
        <Field label="Confirm new password" name="confirm" type="password" required autoComplete="new-password"
          value={v.confirm} onChange={set} />
        <button className="btn lg block" disabled={busy}>{busy ? "Saving…" : "Save new password"}</button>
      </form>
    </div>
  );
}

export default function ResetPasswordPage() {
  return <Suspense><ResetForm /></Suspense>;
}
