"use client";

import Link from "next/link";
import Icon from "@/components/Icon";
import { PageSkeleton, Protected, useAuth } from "@/components/Providers";
import RsvpButton from "@/components/RsvpButton";
import { Avatar, DateChip, Empty, ErrorBox } from "@/components/ui";
import { useApi } from "@/lib/api";
import { firstName, fmt } from "@/lib/format";

function Dashboard() {
  const { user } = useAuth();
  const { data, error, loading, reload } = useApi("/dashboard");
  if (loading && !data) return <PageSkeleton />;

  return (
    <div className="fade-up">
      <section className="welcome glass">
        <div className="welcome-id">
          <Avatar person={user} size="lg" />
          <div>
            <h1>Hello, {firstName(user.name)}</h1>
            <p className="muted" style={{ margin: 0 }}>
              Batch of {user.batch_year} · Class {user.last_class}{user.stream ? ` · ${user.stream}` : ""}{user.city ? ` · ${user.city}` : ""}
            </p>
          </div>
        </div>
        {data && data.completeness < 100 && (
          <Link className="progress glass" href="/profile">
            <span className="between small"><b>Your profile is {data.completeness}% complete</b><Icon name="arrow" size={14} /></span>
            <span className="bar"><i style={{ width: `${data.completeness}%` }} /></span>
            <span className="small faint">Add a photo and details so batchmates can find you.</span>
          </Link>
        )}
      </section>

      <ErrorBox error={error} onRetry={reload} />

      <div className="quick">
        <Link className="glass interactive" href="/directory"><span className="ico-box"><Icon name="search" /></span>Find alumni</Link>
        <Link className="glass interactive" href="/directory?mentor=1"><span className="ico-box"><Icon name="compass" /></span>Find a mentor</Link>
        <Link className="glass interactive" href="/jobs/new"><span className="ico-box"><Icon name="briefcase" /></span>Post a job</Link>
        <Link className="glass interactive" href="/memories"><span className="ico-box"><Icon name="quote" /></span>Share a memory</Link>
      </div>

      {data && (
        <div className="two-col">
          <section className="glass card">
            <div className="card-head"><h2>Upcoming events</h2><Link href="/events">All events <Icon name="arrow" size={14} /></Link></div>
            {data.events.length ? data.events.map((e) => (
              <div className="event-row" key={e.id}>
                <DateChip value={e.starts_at} />
                <div className="grow">
                  <h4><Link href={`/events/${e.id}`}>{e.title}</Link></h4>
                  <p className="faint small" style={{ margin: 0 }}>{e.location} · {e.going} going</p>
                </div>
                <RsvpButton event={e} onChange={reload} />
              </div>
            )) : <Empty icon="calendar" title="No events scheduled">New reunions and talks will show up here.</Empty>}
          </section>

          <section className="glass card">
            <div className="card-head"><h2>Batch of {user.batch_year}</h2><Link href={`/directory?batch=${user.batch_year}`}>See all <Icon name="arrow" size={14} /></Link></div>
            {data.batchmates.length ? (
              <div className="mini-people">
                {data.batchmates.map((p) => (
                  <Link key={p.id} href={`/alumni/${p.id}`}><Avatar person={p} size="md" /><span>{p.name}</span></Link>
                ))}
              </div>
            ) : <Empty icon="users" title="No batchmates here yet">You&apos;re the first from {user.batch_year}. Share the portal with your class.</Empty>}
          </section>

          <section className="glass card">
            <div className="card-head"><h2>Latest opportunities</h2><Link href="/jobs">All jobs <Icon name="arrow" size={14} /></Link></div>
            {data.jobs.length ? data.jobs.map((j) => (
              <div className="list-item" key={j.id}>
                <h4>{j.title}</h4>
                <p className="faint small">{j.company}{j.location ? ` · ${j.location}` : ""} · <span className="tag saffron">{j.job_type}</span></p>
              </div>
            )) : <Empty icon="briefcase" title="No open jobs">Hiring? <Link href="/jobs/new">Post the first one</Link>.</Empty>}
          </section>

          <section className="glass card">
            <div className="card-head"><h2>News from school</h2><Link href="/news">All news <Icon name="arrow" size={14} /></Link></div>
            {data.news.length ? data.news.map((n) => (
              <div className="list-item" key={n.id}>
                <h4>{n.title}</h4>
                <p className="faint small">{fmt(n.created_at)}</p>
              </div>
            )) : <Empty icon="megaphone" title="No news yet" />}
          </section>
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  return <Protected><Dashboard /></Protected>;
}
