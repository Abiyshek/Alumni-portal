"use client";

import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import Icon from "@/components/Icon";
import { NowFields, SchoolFields } from "@/components/ProfileFields";
import { Protected, useAuth, useToast } from "@/components/Providers";
import { Avatar, Field } from "@/components/ui";
import { api } from "@/lib/api";

function EditProfile() {
  const { user, setUser } = useAuth();
  const toast = useToast();
  const router = useRouter();
  const fileRef = useRef(null);
  const [v, setV] = useState(() => {
    const out = {};
    for (const [k, val] of Object.entries(user)) out[k] = val ?? "";
    out.willing_to_mentor = !!user.willing_to_mentor;
    out.show_contact = !!user.show_contact;
    return out;
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k, val) => setV((s) => ({ ...s, [k]: val }));

  async function uploadPhoto(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append("photo", file);
    try {
      const { photo_url } = await api("/profile/photo", { method: "POST", form });
      setUser({ ...user, photo_url });
      toast("Photo updated.");
    } catch (err) {
      toast(err.message, "error");
    }
    e.target.value = "";
  }

  async function save(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const { user: u } = await api("/profile", { method: "PUT", body: v });
      setUser({ ...u, pending_count: user.pending_count });
      toast("Profile saved.");
      router.push(u.status === "approved" ? `/alumni/${u.id}` : "/pending");
    } catch (err) {
      setError(err.message);
      setBusy(false);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  return (
    <div className="auth-wide fade-up">
      <div className="page-head"><div><h1>Edit your profile</h1><p>Batchmates see this in the directory.</p></div></div>
      <form className="glass auth-card" onSubmit={save}>
        {error && <div className="form-error" role="alert">{error}</div>}
        <h2 className="legend">Basics</h2>
        <div className="photo-row">
          <Avatar person={user} size="xl" />
          <div>
            <button type="button" className="btn glass-btn" onClick={() => fileRef.current.click()}><Icon name="camera" size={16} /> Change photo</button>
            <p className="small faint" style={{ marginTop: 8 }}>PNG, JPG or WEBP, up to 3 MB.</p>
            <input ref={fileRef} type="file" accept="image/png,image/jpeg,image/webp" hidden onChange={uploadPhoto} />
          </div>
        </div>
        <div className="grid-2">
          <Field label="Full name" name="name" required value={v.name} onChange={set} />
          <Field label="Email" name="email" value={user.email} onChange={() => {}} disabled hint="To change your email, ask a coordinator." />
        </div>
        <h2 className="legend" style={{ marginTop: 8 }}>School years</h2>
        <SchoolFields v={v} set={set} />
        <h2 className="legend" style={{ marginTop: 8 }}>Today</h2>
        <NowFields v={v} set={set} />
        <div className="form-actions">
          <button className="btn lg" disabled={busy}>{busy ? "Saving…" : "Save profile"}</button>
          <button type="button" className="btn ghost lg" onClick={() => router.back()}>Cancel</button>
        </div>
      </form>
    </div>
  );
}

export default function EditProfilePage() {
  return <Protected level="login"><EditProfile /></Protected>;
}
