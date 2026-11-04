import Link from "next/link";
import { KvLogo } from "@/components/Brand";

export default function NotFound() {
  return (
    <div className="auth glass state-card">
      <KvLogo height={64} />
      <h1 style={{ marginTop: 16 }}>Page not found</h1>
      <p className="muted">This page doesn&apos;t exist or may have moved.</p>
      <Link className="btn" href="/">Back to home</Link>
    </div>
  );
}
