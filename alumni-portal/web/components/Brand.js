// Official logos, taken from the school's website (no2pondicherry.kvs.ac.in, via the gov.in S3WaaS CDN).
export function KvLogo({ height = 56 }) {
  return <img src="/brand/kv-logo.svg" alt="Kendriya Vidyalaya Sangathan logo" height={height} width={Math.round((height * 86) / 69)} />;
}

export function PmShriLogo({ height = 44 }) {
  return <img src="/brand/pm-shri-logo.png" alt="PM SHRI logo" height={height} width={Math.round((height * 170) / 68)} />;
}

export function Brand({ height = 56, compact = false }) {
  return (
    <>
      <KvLogo height={height} />
      <span className="brand-text">
        <strong>PM SHRI Kendriya Vidyalaya No. 2 Pondicherry</strong>
        {!compact && <small>Alumni Association · Kalapet, Puducherry</small>}
      </span>
    </>
  );
}
