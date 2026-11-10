"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { api, setCsrf } from "@/lib/api";
import Icon from "./Icon";

const AuthContext = createContext(null);
const ToastContext = createContext(() => {});

export const useAuth = () => useContext(AuthContext);
export const useToast = () => useContext(ToastContext);

// The last known sign-in is cached in the browser so pages render instantly on the next visit.
// The server stays the source of truth: /api/me re-checks it on every page load and clears a stale cache.
const CACHE_KEY = "kv2-alumni-session";

function readCache() {
  try {
    return JSON.parse(localStorage.getItem(CACHE_KEY)) || null;
  } catch {
    return null;
  }
}

function writeCache(snapshot) {
  try {
    if (snapshot?.user) localStorage.setItem(CACHE_KEY, JSON.stringify(snapshot));
    else localStorage.removeItem(CACHE_KEY);
  } catch {
    // private mode or storage blocked: the site still works, just without the instant start
  }
}

export default function Providers({ children }) {
  const [auth, setAuth] = useState({ user: null, school: null, options: null, loading: true, offline: false });
  const [toasts, setToasts] = useState([]);

  const refresh = useCallback(async () => {
    try {
      const me = await api("/me");
      setCsrf(me.csrf);
      const snapshot = { user: me.user, school: me.school, options: me.options, requireApproval: me.require_approval };
      writeCache(snapshot);
      setAuth({ ...snapshot, loading: false, offline: false });
      return me.user;
    } catch {
      setAuth((a) => ({ ...a, loading: false, offline: true }));
      return null;
    }
  }, []);

  useEffect(() => {
    const cached = readCache();
    if (cached) setAuth({ ...cached, loading: false, offline: false });
    refresh();
  }, [refresh]);

  const setUser = useCallback((user) => setAuth((a) => {
    writeCache({ user, school: a.school, options: a.options, requireApproval: a.requireApproval });
    return { ...a, user };
  }), []);

  const toast = useCallback((message, type = "success") => {
    const id = Math.random().toString(36).slice(2);
    setToasts((t) => [...t, { id, message, type }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 4200);
  }, []);

  return (
    <AuthContext.Provider value={{ ...auth, refresh, setUser }}>
      <ToastContext.Provider value={toast}>
        {children}
        <div className="toasts" role="status" aria-live="polite">
          {toasts.map((t) => (
            <div key={t.id} className={`toast glass ${t.type}`}>
              <Icon className="ico" name={t.type === "error" ? "x" : "check"} />
              <span>{t.message}</span>
            </div>
          ))}
        </div>
      </ToastContext.Provider>
    </AuthContext.Provider>
  );
}

/** Renders children only when the visitor meets `level`: "login" | "approved" | "admin". */
export function Protected({ level = "approved", children }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const path = usePathname();

  const verdict = loading ? "wait"
    : !user ? "login"
    : level !== "login" && user.status !== "approved" ? "pending"
    : level === "admin" && user.role !== "admin" ? "forbidden"
    : "ok";

  useEffect(() => {
    if (verdict === "login") router.replace(`/login?next=${encodeURIComponent(path)}`);
    if (verdict === "pending") router.replace("/pending");
  }, [verdict, router, path]);

  if (verdict === "ok") return children;
  if (verdict === "forbidden") {
    return (
      <div className="auth glass state-card">
        <div className="big"><Icon name="shield" size={34} /></div>
        <h1>Coordinators only</h1>
        <p className="muted">This page is for the school's alumni coordinators. If you need access, ask a coordinator to add you.</p>
      </div>
    );
  }
  return <PageSkeleton />;
}

export function PageSkeleton() {
  return (
    <div aria-busy="true" aria-label="Loading">
      <div className="skeleton" style={{ height: 44, width: 280, marginBottom: 24 }} />
      <div className="two-col">
        <div className="skeleton" style={{ height: 220, marginBottom: 24 }} />
        <div className="skeleton" style={{ height: 220, marginBottom: 24 }} />
      </div>
    </div>
  );
}
