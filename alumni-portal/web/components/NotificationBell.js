"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { fmt } from "@/lib/format";
import { disablePush, enablePush, needsHomeScreen, pushState } from "@/lib/push";
import Icon from "./Icon";
import { useToast } from "./Providers";

const KIND = { news: ["megaphone", "News"], job: ["briefcase", "Job"], event: ["calendar", "Event"] };

export default function NotificationBell() {
  const toast = useToast();
  const path = usePathname();
  const [data, setData] = useState(null);
  const [open, setOpen] = useState(false);
  const [push, setPush] = useState("unsupported");
  const [busy, setBusy] = useState(false);
  const ref = useRef(null);

  const lastLoad = useRef(0);
  const load = useCallback(() => {
    lastLoad.current = Date.now();
    return api("/notifications").then(setData).catch(() => {});
  }, []);

  // Check every 5 minutes, only while the tab is visible, and catch up when the member comes back to it.
  // With many members online, this keeps the bell from becoming most of the server's traffic.
  useEffect(() => {
    load();
    const tick = () => document.visibilityState === "visible" && Date.now() - lastLoad.current > 60000 && load();
    const t = setInterval(tick, 300000);
    document.addEventListener("visibilitychange", tick);
    return () => {
      clearInterval(t);
      document.removeEventListener("visibilitychange", tick);
    };
  }, [load]);

  useEffect(() => {
    pushState().then(setPush).catch(() => setPush("unsupported"));
  }, []);

  useEffect(() => {
    setOpen(false);
  }, [path]);

  useEffect(() => {
    const close = (e) => ref.current && !ref.current.contains(e.target) && setOpen(false);
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  function toggle() {
    const next = !open;
    setOpen(next);
    if (next && data?.unread) {
      // mark as seen on the server, keep the highlights visible while the panel is open
      api("/notifications/seen", { method: "POST" }).then(() => setData((d) => ({ ...d, unread: 0 }))).catch(() => {});
    }
  }

  async function togglePush() {
    setBusy(true);
    try {
      if (push === "on") {
        await disablePush();
        setPush("off");
        toast("Phone notifications turned off.");
      } else {
        await enablePush(data.push_public_key);
        setPush("on");
        toast("Phone notifications are on. You'll be alerted about new news, jobs and events.");
      }
    } catch (e) {
      toast(e.message, "error");
      setPush(await pushState().catch(() => "unsupported"));
    }
    setBusy(false);
  }

  async function toggleEmail() {
    try {
      const r = await api("/notifications/settings", { method: "PUT", body: { notify_email: !data.notify_email } });
      setData((d) => ({ ...d, notify_email: r.notify_email }));
      toast(r.notify_email ? "You'll get emails about new posts." : "Emails about new posts turned off.");
    } catch (e) {
      toast(e.message, "error");
    }
  }

  if (!data) return null;

  return (
    <div className="dropdown bell" ref={ref}>
      <button className="bell-btn" onClick={toggle} aria-expanded={open} aria-haspopup="menu"
        aria-label={data.unread ? `Notifications, ${data.unread} new` : "Notifications"}>
        <Icon name="bell" size={20} />
        {data.unread > 0 && <span className="bell-count">{data.unread > 9 ? "9+" : data.unread}</span>}
      </button>
      {open && (
        <div className="dropdown-menu glass bell-menu" role="menu">
          <div className="bell-head"><b>Notifications</b>{data.items.some((i) => i.unread) && <span className="small faint">New since your last visit</span>}</div>
          <div className="bell-list">
            {data.items.length ? data.items.map((it) => (
              <Link key={`${it.kind}-${it.id}`} href={it.path} className={`bell-item${it.unread ? " unread" : ""}`} role="menuitem">
                <span className="bell-ico"><Icon name={KIND[it.kind][0]} size={16} /></span>
                <span className="grow">
                  <span className="bell-title">{it.title}</span>
                  <span className="small faint">{KIND[it.kind][1]} · {fmt(it.created_at)}</span>
                </span>
              </Link>
            )) : <p className="small faint" style={{ padding: "12px" }}>Nothing new yet. News, jobs and events will show up here.</p>}
          </div>
          <div className="bell-settings">
            <div className="bell-setting">
              <span><b>Phone & browser alerts</b><br />
                <small className="faint">
                  {push === "blocked" ? "Blocked in your browser settings. Allow notifications for this site to turn them on."
                    : push === "unsupported" ? (needsHomeScreen() ? "On iPhone: tap Share → Add to Home Screen, open the app, then turn this on."
                      : "This browser doesn't support push notifications.")
                    : !data.push_public_key ? "Not available on the server yet."
                    : "Get an alert the moment something is posted."}
                </small>
              </span>
              {push !== "unsupported" && push !== "blocked" && data.push_public_key && (
                <button className={`switch${push === "on" ? " on" : ""}`} role="switch" aria-checked={push === "on"}
                  aria-label="Phone and browser alerts" onClick={togglePush} disabled={busy}><i /></button>
              )}
            </div>
            <div className="bell-setting">
              <span><b>Email updates</b><br />
                <small className="faint">{data.email_available ? "An email for each new news post, job and event." : "Your choice is saved. Emails start once the school sets up sending."}</small>
              </span>
              <button className={`switch${data.notify_email ? " on" : ""}`} role="switch" aria-checked={data.notify_email}
                aria-label="Email updates" onClick={toggleEmail}><i /></button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
