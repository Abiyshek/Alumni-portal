"use client";

import { useAuth } from "./Providers";
import { Check, Field } from "./ui";

export function SchoolFields({ v, set }) {
  const { options } = useAuth();
  const year = new Date().getFullYear();
  return (
    <div className="grid-3">
      <Field label="Pass-out year" name="batch_year" type="number" required value={v.batch_year} onChange={set}
        min={1986} max={year + 1} placeholder="e.g. 2015" hint="The year you passed or left school." />
      <Field label="Last class at KV" name="last_class" required value={v.last_class} onChange={set} options={options?.classes || []} blank={null} />
      <Field label="Stream (XI–XII)" name="stream" value={v.stream} onChange={set} options={options?.streams || []} />
      <Field label="House" name="house" value={v.house} onChange={set} placeholder="Your school house" />
      <Field label="Admission no." name="admission_no" value={v.admission_no} onChange={set} hint="Optional, but it helps the school verify you faster." />
    </div>
  );
}

export function NowFields({ v, set }) {
  return (
    <>
      <div className="grid-3">
        <Field label="What you do" name="occupation" value={v.occupation} onChange={set} placeholder="e.g. Engineer, Student" />
        <Field label="Organisation or college" name="organization" value={v.organization} onChange={set} />
        <Field label="Field" name="industry" value={v.industry} onChange={set} placeholder="e.g. Healthcare, IT, Defence" />
        <Field label="City" name="city" value={v.city} onChange={set} />
        <Field label="Country" name="country" value={v.country} onChange={set} />
        <Field label="Phone" name="phone" type="tel" value={v.phone} onChange={set} />
      </div>
      <Field label="LinkedIn or website" name="linkedin" type="url" value={v.linkedin} onChange={set} placeholder="https://" />
      <Field label="About you" name="bio" rows={4} maxLength={1000} value={v.bio} onChange={set}
        placeholder="What have you been up to since school?" />
      <Check name="willing_to_mentor" checked={v.willing_to_mentor} onChange={set}>
        I&apos;m happy to mentor current students and younger alumni
      </Check>
      <Check name="show_contact" checked={v.show_contact} onChange={set}>
        Show my email and phone to verified alumni
      </Check>
    </>
  );
}
