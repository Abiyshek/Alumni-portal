"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import Icon from "@/components/Icon";
import ShareWhatsApp from "@/components/ShareWhatsApp";
import { PageSkeleton, Protected, useAuth, useToast } from "@/components/Providers";
import RsvpButton from "@/components/RsvpButton";
import { Avatar, DateChip, Empty, ErrorBox } from "@/components/ui";
import { api, useApi } from "@/lib/api";
import { fmtLong, fmtTime } from "@/lib/format";

function EventDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const toast = useToast();
  const router = useRouter();
  const { data, error, loading, reload } = useApi(`/events/${id}`);
  if (loading && !data) return <PageSkeleton />;
  if (error) return <ErrorBox error={error} />;
  const { event: e, attendees, is_past } = data;

  async function remove() {
    if (!confirm(`Delete "${e.title}"? This removes all RSVPs and can't be undone.`)) return;
    await api(`/events/${e.id}`, { method: "DELETE" });
    toast("Event deleted.");
    router.push("/events");
  }

  return (
    <div className="fade-up">
      <p><Link href="/events" className="row small"><Icon name="back" size={14} /> All events</Link></p>
      <div className="two-col wide-left">
        <article className="glass card">
          <div className="row" style={{ gap: 18, marginBottom: 16, alignItems: "flex-start" }}>
            <DateChip value={e.starts_at} large />
            <div className="grow">
              <h1 style={{ marginBottom: 8 }}>{e.title}</h1>
              <div className="meta">
                <span><Icon name="clock" size={14} />{fmtLong(e.starts_at)}, {fmtTime(e.starts_at)}</span>
                <span><Icon name="pin" size={14} />{e.location}</span>
              </div>
            </div>
          </div>
          <p className="prewrap muted">{e.description}</p>
          <div className="row" style={{ marginTop: 20 }}>
            {is_past ? <span className="tag">This event has ended</span> : <RsvpButton event={e} onChange={reload} size="lg" />}
            {!is_past && <ShareWhatsApp kind="event" title={e.title} details={`🗓 ${fmtLong(e.starts_at)}, ${fmtTime(e.starts_at)}\n📍 ${e.location}`} path={`/events/${e.id}`} size="lg" />}
            {user.role === "admin" && <button className="btn danger sm" onClick={remove}><Icon name="trash" size={14} /> Delete event</button>}
          </div>
        </article>
        <aside className="glass card">
          <h2>{attendees.length} going</h2>
          {attendees.length ? attendees.map((a) => (
            <Link className="person-line" key={a.id} href={`/alumni/${a.id}`}>
              <Avatar person={a} />
              <span>{a.name}<br /><small className="faint">Batch {a.batch_year}</small></span>
            </Link>
          )) : <Empty icon="users" title="No RSVPs yet">Be the first to say you&apos;re coming.</Empty>}
        </aside>
      </div>
    </div>
  );
}

export default function EventPage() {
  return <Protected><EventDetail /></Protected>;
}
