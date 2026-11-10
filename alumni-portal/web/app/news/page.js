"use client";

import { useState } from "react";
import Icon from "@/components/Icon";
import ShareWhatsApp from "@/components/ShareWhatsApp";
import { PageSkeleton, useAuth, useToast } from "@/components/Providers";
import { Empty, ErrorBox, Field } from "@/components/ui";
import { api, useApi } from "@/lib/api";
import { fmt } from "@/lib/format";

function Composer({ onPosted }) {
  const toast = useToast();
  const [v, setV] = useState({ title: "", body: "" });
  const [busy, setBusy] = useState(false);
  const set = (k, val) => setV((s) => ({ ...s, [k]: val }));

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    try {
      await api("/news", { method: "POST", body: v });
      toast("Announcement published.");
      setV({ title: "", body: "" });
      onPosted();
    } catch (err) {
      toast(err.message, "error");
    }
    setBusy(false);
  }

  return (
    <form className="glass card" onSubmit={submit}>
      <h2 className="legend">Post an announcement</h2>
      <Field label="Headline" name="title" required value={v.title} onChange={set} />
      <Field label="Message" name="body" rows={4} required value={v.body} onChange={set} />
      <button className="btn" disabled={busy}><Icon name="megaphone" size={16} /> {busy ? "Publishing…" : "Publish"}</button>
    </form>
  );
}

export default function NewsPage() {
  const { user } = useAuth();
  const toast = useToast();
  const { data, error, loading, reload } = useApi("/news");
  const admin = user?.role === "admin";

  async function remove(n) {
    if (!confirm(`Delete "${n.title}"? This can't be undone.`)) return;
    await api(`/news/${n.id}`, { method: "DELETE" });
    toast("Announcement deleted.");
    reload();
  }

  return (
    <div className="fade-up" style={{ maxWidth: 820, margin: "0 auto" }}>
      <div className="page-head"><div><h1>News &amp; announcements</h1><p>Updates from the Vidyalaya and the alumni association.</p></div></div>
      {admin && <Composer onPosted={reload} />}
      <ErrorBox error={error} onRetry={reload} />
      {loading && !data ? <PageSkeleton /> : data?.items.length ? data.items.map((n) => (
        <article className="glass card" key={n.id}>
          <span className="eyebrow">{fmt(n.created_at, { day: "numeric", month: "long", year: "numeric" })}</span>
          <h2 style={{ marginTop: 10 }}>{n.title}</h2>
          <p className="prewrap muted">{n.body}</p>
          <div className="between">
            {n.author && <span className="small faint">Posted by {n.author}</span>}
            <span className="row">
              {user?.status === "approved" && <ShareWhatsApp kind="news" title={n.title} details={n.body.length > 200 ? n.body.slice(0, 200) + "…" : n.body} path="/news" />}
              {admin && <button className="btn sm danger" onClick={() => remove(n)}><Icon name="trash" size={13} /> Delete</button>}
            </span>
          </div>
        </article>
      )) : <div className="glass card"><Empty icon="megaphone" title="No announcements yet">News from school will appear here.</Empty></div>}
    </div>
  );
}
