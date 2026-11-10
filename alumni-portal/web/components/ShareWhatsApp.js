"use client";

// Opens WhatsApp (app on phones, WhatsApp Web on computers) with a ready-made message to forward to a group.
export default function ShareWhatsApp({ kind, title, details, path, size = "sm" }) {
  function share() {
    const url = window.location.origin + path;
    const label = { news: "📢 *News from KV No. 2 Pondicherry Alumni*", job: "💼 *New opportunity for KV2 alumni*",
      event: "📅 *Upcoming alumni event*" }[kind];
    const text = [label, "", `*${title}*`, details, "", `🔗 ${url}`].filter((l) => l !== undefined && l !== null).join("\n");
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank", "noopener,noreferrer");
  }
  return (
    <button type="button" className={`btn ${size} whatsapp`} onClick={share} title="Share on WhatsApp">
      <svg width="15" height="15" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor">
        <path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.4a.5.5 0 0 0 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .1-1.3c0-.1-.2-.2-.5-.3z" />
      </svg>
      Share
    </button>
  );
}
