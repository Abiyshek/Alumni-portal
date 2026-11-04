"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Icon from "@/components/Icon";
import { NowFields, SchoolFields } from "@/components/ProfileFields";
import { useAuth, useToast } from "@/components/Providers";
import { Check, Field } from "@/components/ui";
import { api } from "@/lib/api";
import { firstName } from "@/lib/format";

const STEPS = ["Account", "School years", "Today"];

function checkStep(step, v) {
  if (step === 0) {
    if (v.name.trim().length < 2) return "Enter your full name.";
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v.email)) return "Enter a valid email address.";
    if (v.password.length < 8 || !/[A-Za-z]/.test(v.password) || !/\d/.test(v.password))
      return "Use at least 8 characters for your password, with letters and numbers.";
    if (v.password !== v.confirm) return "The two passwords don't match.";
  }
  if (step === 1) {
    const y = Number(v.batch_year);
    if (!y || y < 1986 || y > new Date().getFullYear() + 1) return "Enter the year you passed out (1986 or later).";
  }
  return "";
}

export default function SignupPage() {
  const { user, setUser, requireApproval } = useAuth();
  const toast = useToast();
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [v, setV] = useState({
    name: "", email: "", password: "", confirm: "", batch_year: "", last_class: "XII", stream: "", house: "",
    admission_no: "", occupation: "", organization: "", industry: "", city: "", country: "India", phone: "",
    linkedin: "", bio: "", willing_to_mentor: false, show_contact: false, agree: false,
  });
  const set = (k, val) => setV((s) => ({ ...s, [k]: val }));

  useEffect(() => {
    if (user && !busy) router.replace("/dashboard");
  }, [user, busy, router]);

  async function submit(e) {
    e.preventDefault();
    const problem = checkStep(step, v);
    if (problem) return setError(problem);
    setError("");
    if (step < STEPS.length - 1) return setStep(step + 1);
    if (!v.agree) return setError("Confirm that you studied at KV No. 2 Pondicherry.");
    setBusy(true);
    try {
      const { user: u } = await api("/auth/signup", { method: "POST", body: v });
      setUser(u);
      toast(`Welcome, ${firstName(u.name)}! Your account is ready.`);
      router.push(u.status === "approved" ? "/dashboard" : "/pending");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="auth-wide fade-up">
      <div className="page-head">
        <div>
          <span className="eyebrow">Join the network</span>
          <h1 style={{ marginTop: 10 }}>Register as KV2 alumni</h1>
          <p>It takes about two minutes.{requireApproval && " A coordinator at school checks every new account before it can see the directory."}</p>
        </div>
      </div>
      <form className="glass auth-card" onSubmit={submit} noValidate>
        <div className="stepper" aria-label={`Step ${step + 1} of ${STEPS.length}`}>
          {STEPS.map((s, i) => (
            <div key={s} className={i < step ? "done" : i === step ? "current" : ""}><i /><span>{i + 1}. {s}</span></div>
          ))}
        </div>
        {error && <div className="form-error" role="alert">{error}</div>}

        {step === 0 && (
          <div className="grid-2">
            <Field label="Full name" name="name" required autoComplete="name" value={v.name} onChange={set} />
            <Field label="Email" name="email" type="email" required autoComplete="email" value={v.email} onChange={set} />
            <Field label="Password" name="password" type="password" required autoComplete="new-password" value={v.password} onChange={set}
              hint="At least 8 characters, with letters and numbers." />
            <Field label="Confirm password" name="confirm" type="password" required autoComplete="new-password" value={v.confirm} onChange={set} />
          </div>
        )}
        {step === 1 && <SchoolFields v={v} set={set} />}
        {step === 2 && (
          <>
            <NowFields v={v} set={set} />
            <Check name="agree" checked={v.agree} onChange={set}>
              I studied at PM SHRI Kendriya Vidyalaya No. 2 Pondicherry, and these details are true.
            </Check>
          </>
        )}

        <div className="form-actions">
          {step > 0 && (
            <button type="button" className="btn ghost lg" onClick={() => { setError(""); setStep(step - 1); }}>
              <Icon name="back" size={16} /> Back
            </button>
          )}
          <button className="btn lg" disabled={busy}>
            {step < STEPS.length - 1 ? <>Continue <Icon name="arrow" size={16} /></> : busy ? "Creating your account…" : "Create account"}
          </button>
          <span className="muted small">Already registered? <Link href="/login">Sign in</Link></span>
        </div>
      </form>
    </div>
  );
}
