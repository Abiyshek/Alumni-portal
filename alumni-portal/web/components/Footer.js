import Link from "next/link";
import { KvLogo, PmShriLogo } from "./Brand";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="wrap">
        <div className="footer-grid">
          <div>
            <span className="brand-logo"><KvLogo height={44} /><PmShriLogo height={40} /></span>
            <h4 style={{ textTransform: "none", letterSpacing: 0, fontSize: "1.05rem" }}>PM SHRI Kendriya Vidyalaya No. 2 Pondicherry</h4>
            <p className="small" style={{ maxWidth: 400 }}>
              Alumni Association. Kalapet, Puducherry. Serving students since 1986.
            </p>
            <p className="codes">KV Code 1802 · CBSE Affiliation No. 2900002 · School Code 59203</p>
          </div>
          <div>
            <h4>Alumni</h4>
            <Link href="/directory">Alumni directory</Link>
            <Link href="/events">Events &amp; reunions</Link>
            <Link href="/jobs">Jobs &amp; internships</Link>
            <Link href="/memories">Memories wall</Link>
          </div>
          <div>
            <h4>School</h4>
            <a href="https://no2pondicherry.kvs.ac.in/en/" target="_blank" rel="noopener noreferrer">Official school website ↗</a>
            <Link href="/news">News &amp; announcements</Link>
            <Link href="/signup">Register as alumni</Link>
            <Link href="/login">Alumni login</Link>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} Alumni Association, PM SHRI KV No. 2 Pondicherry</span>
          <span>Kalapet, Puducherry</span>
        </div>
      </div>
    </footer>
  );
}
