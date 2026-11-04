"use client";

import Link from "next/link";
import Icon from "@/components/Icon";
import { PageSkeleton, Protected, useAuth } from "@/components/Providers";
import RsvpButton from "@/components/RsvpButton";
import { DateChip, Empty, ErrorBox } from "@/components/ui";
import { useApi } from "@/lib/api";
import { fmt, fmtLong, fmtTime } from "@/lib/format";

function Events() {
  const { user } = useAuth();
  const { data, error, loading, reload } = useApi("/events");
  if (loading && !data) return <PageSkeleton />;

  return (
    <div className="fade-up">
      <div className="page-head">
        <div><h1>Events &amp; reunions</h1><p>Come back to Kalapet: alumni meets, Annual Day and career talks.</p></div>
        {user.role === "admin" && <Link className="btn" href="/events/new"><Icon name="plus" size={16} /> New event</Link>}
      </div>
      <ErrorBox error={error} onRetry={reload} />

      {data?.upcoming.length ? data.upcoming.map((e) => (
        <article className="glass card event-card interactive" key={e.id}>
          <DateChip value={e.starts_at} large />
          <div className="grow">
            <h3><Link href={`/events/${e.id}`}>{e.title}</Link></h3>
            <div className="meta">
              <span><Icon name="clock" size={14} />{fmtLong(e.starts_at)}, {fmtTime(e.starts_at)}</span>
              <span><Icon name="pin" size={14} />{e.location}</span>
            </div>
            <p className="muted">{e.description.length > 200 ? e.description.slice(0, 200) + "…" : e.description}</p>
            <div className="row">
              <RsvpButton event={e} onChange={reload} />
              <span className="faint small">{e.going} going</span>
            </div>
          </div>
        </article>
      )) : <div className="glass card"><Empty icon="calendar" title="No events scheduled">New reunions and talks will show up here.</Empty></div>}

      {data?.past.length > 0 && (
        <>
          <h2 style={{ marginTop: 36 }}>Past events</h2>
          <div className="glass card">
            {data.past.map((e) => (
              <div className="list-item between" key={e.id}>
                <Link href={`/events/${e.id}`}>{e.title}</Link>
                <span className="faint small">{fmt(e.starts_at)} · {e.going} attended</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default function EventsPage() {
  return <Protected><Events /></Protected>;
}
