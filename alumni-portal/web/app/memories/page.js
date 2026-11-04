"use client";

import Link from "next/link";
import { useState } from "react";
import Icon from "@/components/Icon";
import { PageSkeleton, Protected, useAuth, useToast } from "@/components/Providers";
import { Avatar, Empty, ErrorBox } from "@/components/ui";
import { api, useApi } from "@/lib/api";
import { fmt } from "@/lib/format";

function Memories() {
  const { user } = useAuth();
  const toast = useToast();
  const { data, error, loading, reload } = useApi("/memories");
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);

  async function post(e) {
    e.preventDefault();
    setBusy(true);
    try {
      await api("/memories", { method: "POST", body: { body: text } });
      setText("");
      toast("Pinned to the wall.");
      reload();
    } catch (err) {
      toast(err.message, "error");
    }
    setBusy(false);
  }

  async function remove(m) {
    if (!confirm("Remove this memory from the wall?")) return;
    await api(`/memories/${m.id}`, { method: "DELETE" });
    toast("Memory removed.");
    reload();
  }

  return (
    <div className="fade-up">
      <div className="page-head">
        <div><h1>Memories wall</h1><p>Morning assembly, sports day, Annual Day, the canteen, that one teacher. What do you remember?</p></div>
      </div>
      <form className="glass card" onSubmit={post}>
        <label className="field" htmlFor="memory">
          <span>Your memory</span>
          <textarea id="memory" rows={3} maxLength={2000} required value={text} onChange={(e) => setText(e.target.value)} placeholder="I still remember…" />
        </label>
        <button className="btn" disabled={busy || text.trim().length < 5}><Icon name="quote" size={16} /> {busy ? "Pinning…" : "Pin to the wall"}</button>
      </form>
      <ErrorBox error={error} onRetry={reload} />
      {loading && !data ? <PageSkeleton /> : data?.items.length ? (
        <div className="wall">
          {data.items.map((m) => (
            <article className="memory glass" key={m.id}>
              <span className="quote-mark" aria-hidden="true">&ldquo;</span>
              <p className="prewrap">{m.body}</p>
              <div className="memory-foot">
                <Link className="person-line" href={`/alumni/${m.user_id}`}>
                  <Avatar person={m} />
                  <span>{m.name}<br /><small className="faint">Batch {m.batch_year} · {fmt(m.created_at)}</small></span>
                </Link>
                {(m.user_id === user.id || user.role === "admin") && (
                  <button className="link-btn" onClick={() => remove(m)} aria-label="Remove memory"><Icon name="trash" size={15} /></button>
                )}
              </div>
            </article>
          ))}
        </div>
      ) : <div className="glass card"><Empty icon="quote" title="The wall is empty">Share the first memory.</Empty></div>}
    </div>
  );
}

export default function MemoriesPage() {
  return <Protected><Memories /></Protected>;
}
