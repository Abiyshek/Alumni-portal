"use client";

import Icon from "./Icon";
import { fmtDay, fmtMonth, initials } from "@/lib/format";

export function Avatar({ person, size = "sm" }) {
  if (person?.photo_url) return <img className={`avatar ${size}`} src={person.photo_url} alt="" />;
  return <span className={`avatar ${size}`} aria-hidden="true">{initials(person?.name)}</span>;
}

export function DateChip({ value, large = false }) {
  return (
    <div className={`date-chip${large ? " lg" : ""}`}>
      <b>{fmtDay(value)}</b>
      <span>{fmtMonth(value)}</span>
    </div>
  );
}

export function Empty({ icon = "sparkle", title, children }) {
  return (
    <div className="empty">
      <Icon className="ico" name={icon} size={28} />
      {title && <b>{title}</b>}
      {children && <span className="small">{children}</span>}
    </div>
  );
}

export function ErrorBox({ error, onRetry }) {
  if (!error) return null;
  return (
    <div className="form-error between">
      <span>{error.message}</span>
      {onRetry && <button className="btn sm ghost" onClick={onRetry}>Try again</button>}
    </div>
  );
}

export function Field({ label, name, value, onChange, type = "text", required, hint, options, rows, blank = "Select…", ...rest }) {
  const common = { name, id: name, required, value: value ?? "", onChange: (e) => onChange(name, e.target.value), ...rest };
  let control;
  if (options) {
    control = (
      <select {...common}>
        {blank !== null && <option value="">{blank}</option>}
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    );
  } else if (rows) {
    control = <textarea rows={rows} {...common} />;
  } else {
    control = <input type={type} {...common} />;
  }
  return (
    <label className="field" htmlFor={name}>
      <span>{label}{required && <em> *</em>}</span>
      {control}
      {hint && <small>{hint}</small>}
    </label>
  );
}

export function Check({ name, checked, onChange, children }) {
  return (
    <label className="check">
      <input type="checkbox" name={name} checked={!!checked} onChange={(e) => onChange(name, e.target.checked)} />
      <span>{children}</span>
    </label>
  );
}
