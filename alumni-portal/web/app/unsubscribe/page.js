"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import Icon from "@/components/Icon";
import { api } from "@/lib/api";

function Unsubscribe() {
  const token = useSearchParams().get("token") || "";
  const [state, setState] = useState({ done: false, error: "", busy: false });

  async function confirm() {
    setState({ busy: true });
    try {
      await api("/notifications/unsubscribe", { method: "POST", body: { token } });
      setState({ done: true });
    } catch (e) {
      setState({ error: e.message });
    }
  }

  return (
    <div className="auth glass state-card fade-up">
      <div className="big"><Icon name={state.done ? "check" : "mail"} size={34} /></div>
      {state.done ? (
        <>
          <h1>You&apos;re unsubscribed</h1>
          <p className="muted">You won&apos;t get emails about new posts. You can turn them back on anytime from the 🔔 bell after signing in.</p>
          <Link className="btn" href="/">Go to the portal</Link>
        </>
      ) : (
        <>
          <h1>Stop notification emails?</h1>
          <p className="muted">You&apos;ll stop getting emails when news, jobs or events are posted. Your account stays as it is.</p>
          {state.error && <div className="form-error" role="alert">{state.error}</div>}
          <button className="btn" onClick={confirm} disabled={state.busy}>{state.busy ? "Saving…" : "Yes, stop the emails"}</button>
        </>
      )}
    </div>
  );
}

export default function UnsubscribePage() {
  return <Suspense><Unsubscribe /></Suspense>;
}
