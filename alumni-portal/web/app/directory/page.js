"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import Icon from "@/components/Icon";
import { Protected } from "@/components/Providers";
import { Avatar, Empty, ErrorBox } from "@/components/ui";
import { useApi } from "@/lib/api";
import { roleLine } from "@/lib/format";

function Directory() {
  const params = useSearchParams();
  const router = useRouter();
  const [f, setF] = useState({
    q: params.get("q") || "", batch: params.get("batch") || "", city: params.get("city") || "", mentor: params.get("mentor") === "1",
  });
  const qs = new URLSearchParams(Object.entries({ ...f, mentor: f.mentor ? "1" : "" }).filter(([, v]) => v)).toString();
  const [debounced, setDebounced] = useState(qs);

  useEffect(() => {
    const t = setTimeout(() => {
      setDebounced(qs);
      router.replace(`/directory${qs ? `?${qs}` : ""}`, { scroll: false });
    }, 250);
    return () => clearTimeout(t);
  }, [qs, router]);

  const { data, error, loading, reload } = useApi(`/directory?${debounced}`);
  const set = (k) => (e) => setF((s) => ({ ...s, [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value }));
  const people = data?.people || [];

  return (
    <div className="fade-up">
      <div className="page-head">
        <div>
          <h1>Alumni directory</h1>
          <p>{loading && !data ? "Searching…" : `${people.length} ${people.length === 1 ? "person" : "people"} found`}</p>
        </div>
      </div>

      <div className="filters glass" role="search">
        <div className="search-box">
          <Icon name="search" />
          <input className="input" type="search" placeholder="Search by name, job or company" value={f.q} onChange={set("q")} aria-label="Search" />
        </div>
        <select className="input" value={f.batch} onChange={set("batch")} aria-label="Batch">
          <option value="">All batches</option>
          {(data?.batches || []).map((b) => <option key={b} value={b}>{b}</option>)}
        </select>
        <input className="input city" placeholder="City" value={f.city} onChange={set("city")} aria-label="City" />
        <label className="check"><input type="checkbox" checked={f.mentor} onChange={set("mentor")} /> Mentors only</label>
        {qs && <button className="btn ghost sm" onClick={() => setF({ q: "", batch: "", city: "", mentor: false })}>Clear</button>}
      </div>

      <ErrorBox error={error} onRetry={reload} />

      {people.length ? (
        <div className="people">
          {people.map((p) => (
            <Link className="person glass interactive" key={p.id} href={`/alumni/${p.id}`}>
              <Avatar person={p} size="md" />
              <div className="grow">
                <h3>{p.name}</h3>
                <p className="faint">Batch {p.batch_year}{p.stream && p.stream !== "Not applicable" ? ` · ${p.stream}` : ""}</p>
                {roleLine(p) && <p className="muted">{roleLine(p)}</p>}
                <div className="tags">
                  {p.city && <span className="tag"><Icon name="pin" size={11} />{p.city}</span>}
                  {!!p.willing_to_mentor && <span className="tag saffron">Mentor</span>}
                  {p.role === "admin" && <span className="tag">Coordinator</span>}
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : !loading && (
        <div className="glass card"><Empty icon="search" title="No one matches that search">Try a different name, or clear the filters.</Empty></div>
      )}
    </div>
  );
}

export default function DirectoryPage() {
  return <Protected><Suspense><Directory /></Suspense></Protected>;
}
