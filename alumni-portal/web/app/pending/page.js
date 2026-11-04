"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Icon from "@/components/Icon";
import { Protected, useAuth } from "@/components/Providers";
import { firstName } from "@/lib/format";

function Pending() {
  const { user, refresh } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user.status === "approved") router.replace("/dashboard");
  }, [user, router]);

  return (
    <div className="auth glass state-card fade-up" style={{ maxWidth: 560 }}>
      <div className="big"><Icon name="hourglass" size={34} /></div>
      <h1>You&apos;re almost in, {firstName(user.name)}</h1>
      <p className="muted">
        A coordinator at school is checking your details. Once they approve your account, you can use the
        directory, events, jobs and the memories wall.
      </p>
      <p className="small faint">Batch of {user.batch_year} · Class {user.last_class}{user.stream ? ` · ${user.stream}` : ""}</p>
      <div className="row" style={{ justifyContent: "center", marginTop: 22 }}>
        <Link className="btn" href="/profile">Finish your profile</Link>
        <button className="btn glass-btn" onClick={refresh}>Check again</button>
      </div>
    </div>
  );
}

export default function PendingPage() {
  return <Protected level="login"><Pending /></Protected>;
}
