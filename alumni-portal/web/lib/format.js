// SQLite's datetime('now') values ("YYYY-MM-DD HH:MM:SS") are UTC; event times ("YYYY-MM-DDTHH:MM") are local.
export function parseDate(value) {
  if (!value) return null;
  const d = value.includes(" ") ? new Date(value.replace(" ", "T") + "Z") : new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
}

export function fmt(value, options = { day: "numeric", month: "short", year: "numeric" }) {
  const d = parseDate(value);
  return d ? new Intl.DateTimeFormat("en-IN", options).format(d) : "";
}

export const fmtDay = (v) => fmt(v, { day: "2-digit" });
export const fmtMonth = (v) => fmt(v, { month: "short" });
export const fmtTime = (v) => fmt(v, { hour: "numeric", minute: "2-digit" });
export const fmtLong = (v) => fmt(v, { weekday: "long", day: "numeric", month: "long", year: "numeric" });

export function initials(name = "?") {
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase();
}

export function firstName(name = "") {
  return name.split(/\s+/)[0];
}

export function roleLine(p) {
  if (p.occupation && p.organization) return `${p.occupation} at ${p.organization}`;
  return p.occupation || p.organization || "";
}
