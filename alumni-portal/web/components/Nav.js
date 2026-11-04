"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { firstName } from "@/lib/format";
import { Brand, PmShriLogo } from "./Brand";
import Icon from "./Icon";
import { useAuth, useToast } from "./Providers";
import { Avatar } from "./ui";

const MEMBER_LINKS = [
  ["/dashboard", "Home"],
  ["/directory", "Alumni Directory"],
  ["/events", "Events"],
  ["/jobs", "Jobs"],
  ["/memories", "Memories"],
  ["/news", "News"],
];
const PUBLIC_LINKS = [
  ["/", "Home"],
  ["/news", "News & Announcements"],
  ["/signup", "Register"],
  ["/login", "Alumni Login"],
];

export default function Nav() {
  const { user, setUser } = useAuth();
  const toast = useToast();
  const path = usePathname();
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const accountRef = useRef(null);

  useEffect(() => {
    setMenuOpen(false);
    setAccountOpen(false);
  }, [path]);

  useEffect(() => {
    const close = (e) => accountRef.current && !accountRef.current.contains(e.target) && setAccountOpen(false);
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  const approved = user?.status === "approved";
  const links = approved
    ? [...MEMBER_LINKS, ...(user.role === "admin" ? [["/admin", "Admin"]] : [])]
    : PUBLIC_LINKS;
  const isActive = (href) => path === href || (href !== "/" && path.startsWith(href + "/"));

  async function signOut() {
    await api("/auth/logout", { method: "POST" }).catch(() => {});
    setUser(null);
    toast("You're signed out.");
    router.push("/");
  }

  return (
    <>
      <div className="topstrip">
        <div className="wrap">
          <span><span className="hide-sm">Kendriya Vidyalaya Sangathan · </span>Ministry of Education, Government of India</span>
          <a className="hide-sm" href="https://no2pondicherry.kvs.ac.in/en/" target="_blank" rel="noopener noreferrer">Official school website ↗</a>
        </div>
      </div>

      <header className="brandbar">
        <div className="wrap">
          <Link className="brand" href={approved ? "/dashboard" : "/"} aria-label="Alumni portal home">
            <Brand />
          </Link>
          <div className="brandbar-right">
            <span className="pmshri"><PmShriLogo /></span>
            {user ? (
              <div className="dropdown" ref={accountRef}>
                <button className="dropdown-btn" onClick={() => setAccountOpen((o) => !o)} aria-expanded={accountOpen} aria-haspopup="menu">
                  <Avatar person={user} />
                  <span className="hide-sm">{firstName(user.name)}</span>
                </button>
                {accountOpen && (
                  <div className="dropdown-menu glass" role="menu">
                    <div className="dropdown-head">
                      <b>{user.name}</b>
                      <span className="small faint">Batch of {user.batch_year}</span>
                    </div>
                    <hr />
                    {approved && <Link href={`/alumni/${user.id}`} role="menuitem"><Icon name="user" size={16} />My profile</Link>}
                    <Link href="/profile" role="menuitem"><Icon name="edit" size={16} />Edit profile</Link>
                    <Link href="/password" role="menuitem"><Icon name="key" size={16} />Change password</Link>
                    <hr />
                    <button onClick={signOut} role="menuitem"><Icon name="logout" size={16} />Sign out</button>
                  </div>
                )}
              </div>
            ) : (
              <Link className="btn accent sm hide-sm" href="/signup">Register as alumni</Link>
            )}
          </div>
        </div>
      </header>

      <nav className="navbar" aria-label="Main">
        <div className="wrap">
          <div className={`nav-links${menuOpen ? " open" : ""}`}>
            {links.map(([href, label]) => (
              <Link key={href} href={href} className={isActive(href) ? "on" : ""}>
                {label}
                {href === "/admin" && user?.pending_count > 0 && <span className="badge">{user.pending_count}</span>}
              </Link>
            ))}
          </div>
          <button className="menu-toggle" onClick={() => setMenuOpen((o) => !o)} aria-label="Menu" aria-expanded={menuOpen}>
            <Icon name={menuOpen ? "x" : "menu"} size={20} />
          </button>
        </div>
      </nav>
    </>
  );
}
