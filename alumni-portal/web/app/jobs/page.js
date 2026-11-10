"use client";

import Link from "next/link";
import { useState } from "react";
import Icon from "@/components/Icon";
import ShareWhatsApp from "@/components/ShareWhatsApp";
import { PageSkeleton, Protected, useAuth, useToast } from "@/components/Providers";
import { Empty, ErrorBox } from "@/components/ui";
import { api, useApi } from "@/lib/api";
import { fmt } from "@/lib/format";

function Jobs() {
  const { user, options } = useAuth();
  const toast = useToast();
  const [type, setType] = useState("");
  const { data, error, loading, reload } = useApi(`/jobs${type ? `?type=${encodeURIComponent(type)}` : ""}`);

  async function act(job, action) {
    if (action === "delete" && !confirm(`Delete "${job.title}"? This can't be undone.`)) return;
    try {
      await api(`/jobs/${job.id}/${action}`, { method: "POST" });
      toast({ close: "Listing closed.", reopen: "Listing reopened.", delete: "Listing deleted." }[action]);
      reload();
    } catch (e) {
      toast(e.message, "error");
    }
  }

  return (
    <div className="fade-up">
      <div className="page-head">
        <div><h1>Jobs &amp; opportunities</h1><p>Openings shared by fellow alumni. Hiring? Your juniors are a great place to start.</p></div>
        <Link className="btn" href="/jobs/new"><Icon name="plus" size={16} /> Post an opportunity</Link>
      </div>
      <div className="chips">
        {["", ...(options?.job_types || [])].map((t) => (
          <button key={t || "all"} className={`chip${type === t ? " on" : ""}`} onClick={() => setType(t)}>{t || "All"}</button>
        ))}
      </div>
      <ErrorBox error={error} onRetry={reload} />
      {loading && !data ? <PageSkeleton /> : data?.jobs.length ? data.jobs.map((j) => (
        <article className="glass card job" key={j.id}>
          <div className="between" style={{ alignItems: "flex-start" }}>
            <div>
              <h3>{j.title}</h3>
              <p className="muted" style={{ margin: 0 }}>{j.company}{j.location ? ` · ${j.location}` : ""}</p>
            </div>
            <span className="tag saffron">{j.job_type}</span>
          </div>
          <p className="prewrap muted" style={{ marginTop: 14 }}>{j.description}</p>
          <div className="between">
            <span className="small faint">
              Posted by <Link href={`/alumni/${j.posted_by}`}>{j.poster}</Link> (Batch {j.poster_batch}) · {fmt(j.created_at)}
            </span>
            <span className="row">
              <ShareWhatsApp kind="job" title={`${j.title} at ${j.company}`} details={`${j.job_type}${j.location ? ` · ${j.location}` : ""}`} path="/jobs" />
              {j.apply_link && <a className="btn sm" href={j.apply_link} target="_blank" rel="noopener noreferrer nofollow">Apply <Icon name="external" size={13} /></a>}
              {(j.posted_by === user.id || user.role === "admin") && (
                <>
                  <button className="btn sm ghost" onClick={() => act(j, "close")}>Close listing</button>
                  <button className="btn sm danger" onClick={() => act(j, "delete")}>Delete</button>
                </>
              )}
            </span>
          </div>
        </article>
      )) : (
        <div className="glass card"><Empty icon="briefcase" title={type ? `No open ${type.toLowerCase()} roles` : "No open opportunities"}>Know of an opening? Post it for fellow alumni.</Empty></div>
      )}

      {data?.closed_mine.length > 0 && (
        <>
          <h2 style={{ marginTop: 36 }}>Your closed listings</h2>
          <div className="glass card">
            {data.closed_mine.map((j) => (
              <div className="list-item between" key={j.id}>
                <span>{j.title} <span className="faint">· {j.company}</span></span>
                <button className="btn sm ghost" onClick={() => act(j, "reopen")}>Reopen</button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default function JobsPage() {
  return <Protected><Jobs /></Protected>;
}
