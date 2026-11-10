"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import Icon from "@/components/Icon";
import { PageSkeleton, Protected, useAuth } from "@/components/Providers";
import { Avatar, Empty, ErrorBox } from "@/components/ui";
import { useApi } from "@/lib/api";
import { firstName, roleLine } from "@/lib/format";

function Profile() {
  const { id } = useParams();
  const { user } = useAuth();
  const { data, error, loading } = useApi(`/alumni/${id}`);
  if (loading) return <PageSkeleton />;
  if (error) return <ErrorBox error={error} />;
  const { person: p, memories, jobs } = data;
  const me = p.id === user.id;

  return (
    <div className="fade-up">
      <p><Link href="/directory" className="row small"><Icon name="back" size={14} /> Back to directory</Link></p>
      <section className="profile-hero glass">
        <Avatar person={p} size="xl" />
        <div className="grow">
          <h1>{p.name}</h1>
          {roleLine(p) && <p style={{ fontSize: "1.08rem", margin: "0 0 4px" }}>{roleLine(p)}</p>}
          <p className="muted" style={{ margin: 0 }}>
            Batch of {p.batch_year} · Class {p.last_class}
            {p.stream && p.stream !== "Not applicable" ? ` · ${p.stream}` : ""}{p.house ? ` · ${p.house} House` : ""}
          </p>
          <div className="row" style={{ marginTop: 12 }}>
            {!!p.willing_to_mentor && <span className="tag saffron"><Icon name="compass" size={12} /> Open to mentoring</span>}
            {p.industry && <span className="tag">{p.industry}</span>}
            {p.city && <span className="tag"><Icon name="pin" size={12} /> {p.city}{p.country ? `, ${p.country}` : ""}</span>}
          </div>
        </div>
        {me && <Link className="btn glass-btn" href="/profile"><Icon name="edit" size={16} /> Edit profile</Link>}
      </section>

      <div className="two-col wide-left">
        <section className="glass card">
          <h2>About</h2>
          {p.bio ? <p className="prewrap muted">{p.bio}</p> : <Empty icon="user" title={me ? "Add a few lines about yourself" : "No bio yet"} />}
          {memories.length > 0 && (
            <>
              <h3 style={{ marginTop: 24 }}>Memories shared</h3>
              {memories.map((m) => (
                <div key={m.id}>
                  {m.image_url && <img className="profile-memory-image" src={m.image_url} alt={m.body ? m.body.slice(0, 120) : "Shared photo"} loading="lazy" />}
                  {m.body && <blockquote>{m.body}</blockquote>}
                </div>
              ))}
            </>
          )}
        </section>
        <section className="glass card">
          <h2>Contact</h2>
          {p.email ? (
            <>
              <div className="contact-line"><Icon name="mail" /><a href={`mailto:${p.email}`}>{p.email}</a></div>
              {p.phone && <div className="contact-line"><Icon name="phone" />{p.phone}</div>}
            </>
          ) : <p className="muted">{firstName(p.name)} keeps their contact details private.</p>}
          {p.linkedin && (
            <div className="contact-line"><Icon name="link" /><a href={p.linkedin} target="_blank" rel="noopener noreferrer nofollow">{p.linkedin.replace(/^https?:\/\//, "")}</a></div>
          )}
          {jobs.length > 0 && (
            <>
              <h3 style={{ marginTop: 20 }}>Open opportunities</h3>
              {jobs.map((j) => <p key={j.id} className="small"><Link href="/jobs">{j.title}</Link> <span className="faint">· {j.company}</span></p>)}
            </>
          )}
        </section>
      </div>
    </div>
  );
}

export default function ProfilePage() {
  return <Protected><Profile /></Protected>;
}
