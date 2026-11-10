"use client";

import { useCallback, useEffect, useState } from "react";

// The Flask session cookie authenticates requests; state-changing calls also carry the CSRF token.
let csrfToken = "";

export function setCsrf(token) {
  if (token) csrfToken = token;
}

export async function api(path, options = {}) {
  try {
    return await request(path, options);
  } catch (err) {
    // A stale token (e.g. a tab left open while the session changed): get a fresh one and retry once.
    if (err.status === 400 && err.csrfRejected && path !== "/me") {
      await request("/me");
      return request(path, options);
    }
    throw err;
  }
}

async function request(path, { method = "GET", body, form } = {}) {
  const headers = {};
  let payload;
  if (method !== "GET") headers["X-CSRF-Token"] = csrfToken;
  if (form) {
    payload = form;
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }
  let res;
  try {
    res = await fetch(`/api${path}`, { method, headers, body: payload, credentials: "same-origin", cache: "no-store" });
  } catch {
    throw Object.assign(new Error("Can't reach the server. Check that the backend is running, then try again."), { status: 0 });
  }
  const data = await res.json().catch(() => ({}));
  setCsrf(data.csrf);
  if (!res.ok) {
    throw Object.assign(new Error(data.error || "Something went wrong. Please try again."), {
      status: res.status,
      csrfRejected: res.status === 400 && /form token/i.test(data.error || ""),
    });
  }
  return data;
}

export function useApi(path) {
  const [state, setState] = useState({ data: null, error: null, loading: true });

  const load = useCallback(async () => {
    if (!path) return;
    setState((s) => ({ ...s, loading: true }));
    try {
      setState({ data: await api(path), error: null, loading: false });
    } catch (error) {
      setState({ data: null, error, loading: false });
    }
  }, [path]);

  useEffect(() => {
    load();
  }, [load]);

  return { ...state, reload: load };
}
