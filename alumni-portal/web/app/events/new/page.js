"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Protected, useToast } from "@/components/Providers";
import { Field } from "@/components/ui";
import { api } from "@/lib/api";

function NewEvent() {
  const router = useRouter();
  const toast = useToast();
  const [v, setV] = useState({ title: "", starts_at: "", location: "", description: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k, val) => setV((s) => ({ ...s, [k]: val }));

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const { id } = await api("/events", { method: "POST", body: v });
      toast("Event published. Alumni can RSVP now.");
      router.push(`/events/${id}`);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="auth-wide fade-up">
      <div className="page-head"><div><h1>Create an event</h1><p>Every verified alum will see it on their dashboard.</p></div></div>
      <form className="glass auth-card" onSubmit={submit}>
        {error && <div className="form-error" role="alert">{error}</div>}
        <Field label="Event name" name="title" required value={v.title} onChange={set} placeholder="e.g. Silver Jubilee Reunion, Batch of 2000" />
        <div className="grid-2">
          <Field label="Date and time" name="starts_at" type="datetime-local" required value={v.starts_at} onChange={set} />
          <Field label="Venue" name="location" required value={v.location} onChange={set} placeholder="e.g. School Auditorium, Kalapet" />
        </div>
        <Field label="Description" name="description" rows={6} required value={v.description} onChange={set}
          placeholder="What's planned, who it's for, and anything people should bring." />
        <div className="form-actions">
          <button className="btn lg" disabled={busy}>{busy ? "Publishing…" : "Publish event"}</button>
          <button type="button" className="btn ghost lg" onClick={() => router.back()}>Cancel</button>
        </div>
      </form>
    </div>
  );
}

export default function NewEventPage() {
  return <Protected level="admin"><NewEvent /></Protected>;
}
