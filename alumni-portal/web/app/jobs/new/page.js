"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Protected, useAuth, useToast } from "@/components/Providers";
import { Field } from "@/components/ui";
import { api } from "@/lib/api";

function NewJob() {
  const { options } = useAuth();
  const router = useRouter();
  const toast = useToast();
  const [v, setV] = useState({ title: "", company: "", location: "", job_type: "Full-time", description: "", apply_link: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k, val) => setV((s) => ({ ...s, [k]: val }));

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api("/jobs", { method: "POST", body: v });
      toast("Opportunity posted. Thanks for helping fellow alumni!");
      router.push("/jobs");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="auth-wide fade-up">
      <div className="page-head"><div><h1>Post an opportunity</h1><p>Jobs, internships or freelance work for KV2 alumni.</p></div></div>
      <form className="glass auth-card" onSubmit={submit}>
        {error && <div className="form-error" role="alert">{error}</div>}
        <div className="grid-2">
          <Field label="Role" name="title" required value={v.title} onChange={set} placeholder="e.g. Summer Intern, Web Development" />
          <Field label="Organisation" name="company" required value={v.company} onChange={set} />
          <Field label="Location" name="location" value={v.location} onChange={set} placeholder="City, or Remote" />
          <Field label="Type" name="job_type" required value={v.job_type} onChange={set} options={options?.job_types || []} blank={null} />
        </div>
        <Field label="Description" name="description" rows={6} required value={v.description} onChange={set}
          placeholder="What the role involves, who can apply, and how to reach you." />
        <Field label="Application link" name="apply_link" type="url" value={v.apply_link} onChange={set} placeholder="https://" hint="Optional." />
        <div className="form-actions">
          <button className="btn lg" disabled={busy}>{busy ? "Posting…" : "Post opportunity"}</button>
          <button type="button" className="btn ghost lg" onClick={() => router.back()}>Cancel</button>
        </div>
      </form>
    </div>
  );
}

export default function NewJobPage() {
  return <Protected><NewJob /></Protected>;
}
