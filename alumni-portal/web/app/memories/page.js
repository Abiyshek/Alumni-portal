"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import Icon from "@/components/Icon";
import { PageSkeleton, Protected, useAuth, useToast } from "@/components/Providers";
import { Avatar, Empty, ErrorBox } from "@/components/ui";
import { api, useApi } from "@/lib/api";
import { fmt } from "@/lib/format";
import { shrinkImage } from "@/lib/image";

function Memories() {
  const { user } = useAuth();
  const toast = useToast();
  const { data, error, loading, reload } = useApi("/memories");
  const [text, setText] = useState("");
  const [photo, setPhoto] = useState(null); // { blob, preview }
  const [busy, setBusy] = useState(false);
  const fileRef = useRef(null);

  useEffect(() => () => photo && URL.revokeObjectURL(photo.preview), [photo]);

  async function pickPhoto(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    try {
      const blob = await shrinkImage(file);
      setPhoto({ blob, preview: URL.createObjectURL(blob) });
    } catch (err) {
      toast(err.message, "error");
    }
  }

  async function post(e) {
    e.preventDefault();
    setBusy(true);
    try {
      if (photo) {
        const form = new FormData();
        form.append("body", text);
        form.append("image", photo.blob, "memory.jpg");
        await api("/memories", { method: "POST", form });
      } else {
        await api("/memories", { method: "POST", body: { body: text } });
      }
      setText("");
      setPhoto(null);
      toast("Pinned to the wall.");
      reload();
    } catch (err) {
      toast(err.message, "error");
    }
    setBusy(false);
  }

  const canPost = photo || text.trim().length >= 5;

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
          <textarea id="memory" rows={3} maxLength={2000} value={text} onChange={(e) => setText(e.target.value)}
            placeholder={photo ? "Add a caption: who, where, which year…" : "I still remember…"} />
        </label>
        {photo && (
          <div className="photo-preview">
            <img src={photo.preview} alt="Selected photo" />
            <button type="button" className="link-btn" onClick={() => setPhoto(null)}><Icon name="x" size={15} /> Remove photo</button>
          </div>
        )}
        <div className="row">
          <button className="btn" disabled={busy || !canPost}><Icon name="quote" size={16} /> {busy ? "Pinning…" : "Pin to the wall"}</button>
          <button type="button" className="btn outline" onClick={() => fileRef.current.click()} disabled={busy}>
            <Icon name="camera" size={16} /> {photo ? "Change photo" : "Add a photo"}
          </button>
          <input ref={fileRef} type="file" accept="image/*" hidden onChange={pickPhoto} />
        </div>
      </form>
      <ErrorBox error={error} onRetry={reload} />
      {loading && !data ? <PageSkeleton /> : data?.items.length ? (
        <div className="wall">
          {data.items.map((m) => (
            <article className={`memory glass${m.image_url ? " has-image" : ""}`} key={m.id}>
              {m.image_url ? (
                <a href={m.image_url} target="_blank" rel="noopener noreferrer" className="memory-image">
                  <img src={m.image_url} alt={m.body ? m.body.slice(0, 120) : `Photo shared by ${m.name}`} loading="lazy" />
                </a>
              ) : <span className="quote-mark" aria-hidden="true">&ldquo;</span>}
              {m.body && <p className="prewrap">{m.body}</p>}
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
