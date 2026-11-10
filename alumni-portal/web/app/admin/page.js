"use client";

import Link from "next/link";
import { useState } from "react";
import Icon from "@/components/Icon";
import { PageSkeleton, Protected, useAuth, useToast } from "@/components/Providers";
import { Avatar, Empty, ErrorBox } from "@/components/ui";
import { api, useApi } from "@/lib/api";
import { fmt } from "@/lib/format";

const TABS = ["pending", "approved", "suspended", "rejected", "all"];
const ACTIONS = { pending: ["approve", "reject"], approved: ["suspend"], suspended: ["restore"], rejected: ["approve"] };
const LABELS = { approve: "Approve", reject: "Reject", suspend: "Suspend", restore: "Restore", make_admin: "Make coordinator", remove_admin: "Remove coordinator" };
const DONE = { approve: "approved", reject: "rejected", suspend: "suspended", restore: "restored", make_admin: "is now a coordinator", remove_admin: "is no longer a coordinator", delete: "deleted" };

function Admin() {
  const { user: me, refresh } = useAuth();
  const toast = useToast();
  const [tab, setTab] = useState("pending");
  const { data, error, loading, reload } = useApi(`/admin?status=${tab}`);

  async function act(u, action) {
    if (action === "delete" && !confirm(`Permanently delete ${u.name}'s account? This can't be undone.`)) return;
    try {
      await api(`/admin/users/${u.id}/${action}`, { method: "POST" });
      toast(`${u.name} ${DONE[action]}.`);
      reload();
      refresh();
    } catch (e) {
      toast(e.message, "error");
    }
  }

  async function setAutoApprove(on) {
    try {
      await api("/admin/settings", { method: "POST", body: { auto_approve: on } });
      toast(on ? "New registrations are now approved automatically." : "New registrations will wait for approval again.");
      reload();
    } catch (e) {
      toast(e.message, "error");
    }
  }

  async function approveAllPending() {
    const n = data?.counts?.pending || 0;
    if (!confirm(`Approve all ${n} pending registration${n === 1 ? "" : "s"}? They'll get full access to the directory.`)) return;
    try {
      const r = await api("/admin/approve-pending", { method: "POST" });
      toast(`Approved ${r.approved} registration${r.approved === 1 ? "" : "s"}.`);
      reload();
      refresh();
    } catch (e) {
      toast(e.message, "error");
    }
  }

  const [resetLinks, setResetLinks] = useState({});

  async function makeResetLink(u) {
    try {
      const r = await api(`/admin/users/${u.id}/reset-link`, { method: "POST" });
      const url = window.location.origin + r.path;
      setResetLinks((links) => ({ ...links, [u.id]: url }));
      await copy(url, `Reset link for ${u.name} copied. It works once, for ${r.hours} hours.`);
    } catch (e) {
      toast(e.message, "error");
    }
  }

  async function copy(text, message = "Copied.") {
    try {
      await navigator.clipboard.writeText(text);
      toast(message);
    } catch {
      toast("Couldn't copy automatically. Select the link and copy it.", "error");
    }
  }

  const counts = data?.counts || {};
  const maxBatch = Math.max(1, ...(data?.by_batch || []).map((b) => b.c));

  return (
    <div className="fade-up">
      <div className="page-head">
        <div><h1>Administration</h1><p>Verify new registrations and manage the alumni network.</p></div>
        <div className="row">
          <Link className="btn glass-btn" href="/news">Post news</Link>
          <Link className="btn" href="/events/new"><Icon name="plus" size={16} /> New event</Link>
        </div>
      </div>

      <div className="stats-grid">
        {[[counts.pending || 0, "waiting for approval"], [counts.approved || 0, "verified alumni"], [data?.totals.events ?? "–", "events"],
          [data?.totals.jobs ?? "–", "open jobs"], [data?.totals.memories ?? "–", "memories"]].map(([n, label]) => (
          <div className="stat glass" key={label}><b>{n}</b><span>{label}</span></div>
        ))}
      </div>

      <ErrorBox error={error} onRetry={reload} />

      {data && (
        <section className="glass card setting-row">
          <div className="grow">
            <h2>Approve new registrations automatically</h2>
            <p className="muted small" style={{ margin: 0 }}>
              {data.settings.auto_approve
                ? "On: new alumni get full access as soon as they register. Turn it off if you see signups from people who didn't study here."
                : "Off: new registrations wait in Pending until a coordinator approves them."}
            </p>
          </div>
          <div className="row">
            {counts.pending > 0 && (
              <button className="btn sm outline" onClick={approveAllPending}>Approve all pending ({counts.pending})</button>
            )}
            <button className={`switch${data.settings.auto_approve ? " on" : ""}`} role="switch" aria-checked={data.settings.auto_approve}
              aria-label="Approve new registrations automatically" onClick={() => setAutoApprove(!data.settings.auto_approve)}>
              <i />
            </button>
          </div>
        </section>
      )}

      <div>
        <section className="glass card">
          <div className="chips">
            {TABS.map((t) => (
              <button key={t} className={`chip${tab === t ? " on" : ""}`} onClick={() => setTab(t)}>
                {t[0].toUpperCase() + t.slice(1)}{t !== "all" ? ` (${counts[t] || 0})` : ""}
              </button>
            ))}
          </div>
          {loading && !data ? <PageSkeleton /> : data?.users.length ? (
            <div className="table-wrap">
              <table>
                <thead><tr><th>Name</th><th>Batch</th><th>Details</th><th>Joined</th><th aria-label="Actions" /></tr></thead>
                <tbody>
                  {data.users.map((u) => (
                    <tr key={u.id}>
                      <td>
                        <div className="person-line" style={{ padding: 0 }}>
                          <Avatar person={u} />
                          <span><b>{u.name}</b>{u.role === "admin" && <> <span className="tag saffron">coordinator</span></>}<br /><small className="faint">{u.email}</small></span>
                        </div>
                      </td>
                      <td>{u.batch_year}<br /><small className="faint">Class {u.last_class}</small></td>
                      <td className="small muted">
                        {u.stream}{u.admission_no && <><br />Adm. no. {u.admission_no}</>}{u.city && <><br />{u.city}</>}
                      </td>
                      <td className="small">{fmt(u.created_at)}<br /><span className={`tag ${u.status}`}>{u.status}</span></td>
                      <td>
                        {u.id === me.id ? <span className="faint small">You</span> : (
                          <div className="actions-cell">
                            {ACTIONS[u.status].map((a) => (
                              <button key={a} className={`btn sm ${a === "reject" || a === "suspend" ? "danger" : ""}`} onClick={() => act(u, a)}>{LABELS[a]}</button>
                            ))}
                            {u.status === "approved" && (
                              <button className="btn sm ghost" onClick={() => act(u, u.role === "admin" ? "remove_admin" : "make_admin")}>
                                {LABELS[u.role === "admin" ? "remove_admin" : "make_admin"]}
                              </button>
                            )}
                            <button className="btn sm ghost" onClick={() => makeResetLink(u)}><Icon name="key" size={14} /> Reset password</button>
                            <button className="link-btn" onClick={() => act(u, "delete")} aria-label={`Delete ${u.name}`}><Icon name="trash" size={15} /></button>
                          </div>
                        )}
                        {resetLinks[u.id] && (
                          <div className="reset-link">
                            <code title={resetLinks[u.id]}>{resetLinks[u.id]}</code>
                            <button className="btn sm outline" onClick={() => copy(resetLinks[u.id])}><Icon name="copy" size={13} /> Copy</button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : <Empty icon="check" title={tab === "pending" ? "You're all caught up" : "No one here"}>{tab === "pending" ? "No registrations are waiting for approval." : ""}</Empty>}
        </section>

        <aside className="glass card">
          <h2>Alumni by batch</h2>
          {data?.by_batch.length ? data.by_batch.map((b) => (
            <div className="bar-row" key={b.batch_year}>
              <span>{b.batch_year}</span>
              <span className="bar"><i style={{ width: `${(b.c / maxBatch) * 100}%` }} /></span>
              <b>{b.c}</b>
            </div>
          )) : <Empty icon="users" title="No verified alumni yet" />}
        </aside>
      </div>
    </div>
  );
}

export default function AdminPage() {
  return <Protected level="admin"><Admin /></Protected>;
}
