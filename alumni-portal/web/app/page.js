"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import Icon from "@/components/Icon";
import { useAuth } from "@/components/Providers";
import { DateChip, Empty } from "@/components/ui";
import { useApi } from "@/lib/api";
import { fmt, fmtLong, fmtTime } from "@/lib/format";

const HeroScene = dynamic(() => import("@/components/HeroScene"), { ssr: false });

const FEATURES = [
  ["users", "Alumni directory", "Find classmates by batch, city or profession and get back in touch."],
  ["calendar", "Reunions & events", "Stay informed about alumni meets, Annual Day and career talks on campus."],
  ["briefcase", "Jobs & internships", "Share openings at your organisation with fellow Vidyalaya alumni."],
  ["compass", "Mentorship", "Guide Class XII students as they choose colleges and careers."],
];

const FACTS = [
  ["Established", "1986"],
  ["Location", "Kalapet, Puducherry"],
  ["Affiliation", "CBSE, No. 2900002"],
  ["KV Code", "1802"],
  ["School Code", "59203"],
];

export default function Home() {
  const { user } = useAuth();
  const { data } = useApi("/home");
  const stats = data?.stats;
  const nextEvent = data?.events?.[0];

  return (
    <div className="home">
      <section className="main-hero bleed">
        <div className="hero-canvas"><HeroScene /></div>
        <div className="wrap">
          <div className="hero">
            <div className="fade-up">
              <span className="eyebrow">Alumni Association</span>
              <h1>Welcome back to <span>KV No. 2 Pondicherry</span></h1>
              <p className="lead">
                The official alumni portal of PM SHRI Kendriya Vidyalaya No. 2 Pondicherry, Kalapet. Reconnect with
                your batchmates and teachers, and support the students who walk the same corridors today.
              </p>
              <div className="hero-actions">
                {user ? (
                  <Link className="btn lg" href={user.status === "approved" ? "/dashboard" : "/pending"}>
                    Go to your dashboard <Icon name="arrow" size={18} />
                  </Link>
                ) : (
                  <>
                    <Link className="btn lg accent" href="/signup">Register as alumni</Link>
                    <Link className="btn lg outline" href="/login">Alumni login</Link>
                  </>
                )}
              </div>
            </div>

            <aside className="glass hero-panel fade-up">
              <h3>The network today</h3>
              <div className="hero-stats">
                {[["alumni", "Verified alumni"], ["batches", "Batches"], ["mentors", "Mentors"], ["events", "Upcoming events"]].map(([k, label]) => (
                  <div className="stat" key={k}><b>{stats ? stats[k] : "–"}</b><span>{label}</span></div>
                ))}
              </div>
              {nextEvent && (
                <div className="next-event">
                  <DateChip value={nextEvent.starts_at} />
                  <div>
                    <span className="small faint">Next event</span>
                    <h4>{nextEvent.title}</h4>
                    <span className="small muted">{nextEvent.location}</span>
                  </div>
                </div>
              )}
            </aside>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-head center center-text" style={{ textAlign: "center" }}>
          <span className="eyebrow">Why join</span>
          <h2>Stay connected to your Vidyalaya</h2>
          <p>Everything an alumnus needs, in one place.</p>
        </div>
        <div className="features">
          {FEATURES.map(([icon, title, text]) => (
            <div className="feature glass interactive" key={title}>
              <div className="ico-box"><Icon name={icon} size={22} /></div>
              <h3>{title}</h3>
              <p>{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section alt bleed">
        <div className="wrap about">
          <div>
            <span className="eyebrow">About the Vidyalaya</span>
            <h2 style={{ fontSize: "clamp(1.6rem, 2.8vw, 2.1rem)", margin: "16px 0 16px" }}>PM SHRI Kendriya Vidyalaya No. 2 Pondicherry</h2>
            <p>
              Established in 1986 at Kalapet, the Vidyalaya is part of Kendriya Vidyalaya Sangathan under the Ministry of
              Education, Government of India. Generations of students have passed through its classrooms and gone on to
              serve in every field.
            </p>
            <p>This portal brings them together again.</p>
            <div className="motto-line">
              <b lang="sa">तत् त्वं पूषन् अपावृणु</b>
              <span>The motto of Kendriya Vidyalaya Sangathan</span>
            </div>
          </div>
          <dl className="glass facts">
            {FACTS.map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}
          </dl>
        </div>
      </section>

      <section className="section">
        <div className="section-head center" style={{ textAlign: "center" }}>
          <span className="eyebrow">How to join</span>
          <h2>Three simple steps</h2>
        </div>
        <div className="steps">
          <div className="step glass"><h3>Register</h3><p>Fill in your pass-out year, last class and stream. It takes about two minutes.</p></div>
          <div className="step glass"><h3>Get verified</h3><p>The alumni coordinator at school confirms your details, usually within a few days.</p></div>
          <div className="step glass"><h3>Reconnect</h3><p>Browse the directory, RSVP for events and share opportunities.</p></div>
        </div>
      </section>

      <section className="section alt bleed">
        <div className="wrap two-col">
          <div className="glass card">
            <div className="card-head"><h2>News &amp; announcements</h2><Link href="/news">View all <Icon name="arrow" size={14} /></Link></div>
            {data?.news?.length ? data.news.map((n) => (
              <article className="list-item" key={n.id}>
                <p className="faint small" style={{ marginBottom: 4 }}>{fmt(n.created_at, { day: "numeric", month: "long", year: "numeric" })}</p>
                <h4>{n.title}</h4>
                <p className="muted small">{n.body.length > 140 ? n.body.slice(0, 140) + "…" : n.body}</p>
              </article>
            )) : <Empty icon="megaphone" title="No announcements yet">News from school will appear here.</Empty>}
          </div>
          <div className="glass card">
            <div className="card-head"><h2>Upcoming events</h2>{user && <Link href="/events">View all <Icon name="arrow" size={14} /></Link>}</div>
            {data?.events?.length ? data.events.map((e) => (
              <div className="event-row" key={e.id}>
                <DateChip value={e.starts_at} />
                <div><h4>{e.title}</h4><p className="faint small" style={{ margin: 0 }}>{fmtLong(e.starts_at)}, {fmtTime(e.starts_at)} · {e.location}</p></div>
              </div>
            )) : <Empty icon="calendar" title="No events scheduled">New reunions and talks will be listed here.</Empty>}
          </div>
        </div>
      </section>

      {!user && (
        <section className="section">
          <div className="cta-band">
            <div>
              <h2>Studied at KV No. 2 Pondicherry?</h2>
              <p>Register today. Your batchmates may already be here.</p>
            </div>
            <Link className="btn lg accent" href="/signup">Register as alumni <Icon name="arrow" size={18} /></Link>
          </div>
        </section>
      )}
    </div>
  );
}
