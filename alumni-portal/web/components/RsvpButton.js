"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import Icon from "./Icon";
import { useToast } from "./Providers";

export default function RsvpButton({ event, onChange, size = "sm" }) {
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  async function toggle() {
    setBusy(true);
    try {
      const r = await api(`/events/${event.id}/rsvp`, { method: "POST" });
      toast(r.mine ? "You're going. See you there!" : "RSVP cancelled.");
      onChange?.(r);
    } catch (e) {
      toast(e.message, "error");
    }
    setBusy(false);
  }
  return (
    <button className={`btn ${size} ${event.mine ? "on" : ""}`} onClick={toggle} disabled={busy}>
      {event.mine ? <><Icon name="check" size={14} /> Going</> : "RSVP"}
    </button>
  );
}
