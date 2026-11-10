"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { KvLogo } from "@/components/Brand";
import { useAuth, useToast } from "@/components/Providers";
import { Check, Field } from "@/components/ui";
import { api } from "@/lib/api";
import { firstName } from "@/lib/format";

function LoginForm() {
  const { user, setUser } = useAuth();
  const toast = useToast();
  const router = useRouter();
  const params = useSearchParams();
  const [v, setV] = useState({ email: "", password: "", remember: false });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k, val) => setV((s) => ({ ...s, [k]: val }));

  const next = params.get("next");
  const dest = (u) => (u.status !== "approved" ? "/pending" : next && next.startsWith("/") && !next.startsWith("//") ? next : "/dashboard");

  useEffect(() => {
    if (user) router.replace(dest(user));
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const { user: u } = await api("/auth/login", { method: "POST", body: v });
      toast(`Welcome back, ${firstName(u.name)}.`);
      setUser(u);
      router.push(dest(u));
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="auth fade-up">
      <div className="auth-head">
        <KvLogo height={72} />
        <h1>Welcome back</h1>
        <p>Sign in to the PM SHRI KV No. 2 Pondicherry alumni portal.</p>
      </div>
      <form className="glass auth-card" onSubmit={submit}>
        {error && <div className="form-error" role="alert">{error}</div>}
        <Field label="Email" name="email" type="email" required autoFocus autoComplete="email" value={v.email} onChange={set} />
        <Field label="Password" name="password" type="password" required autoComplete="current-password" value={v.password} onChange={set} />
        <Check name="remember" checked={v.remember} onChange={set}>Keep me signed in for 7 days</Check>
        <button className="btn lg block" disabled={busy} style={{ marginTop: 12 }}>{busy ? "Signing in…" : "Sign in"}</button>
        <p className="small faint center" style={{ marginTop: 16, marginBottom: 0 }}>
          Forgot your password? Ask the alumni coordinator for a reset link.
        </p>
      </form>
      <p className="center muted" style={{ marginTop: 20 }}>New here? <Link href="/signup">Register as alumni</Link></p>
    </div>
  );
}

export default function LoginPage() {
  return <Suspense><LoginForm /></Suspense>;
}
