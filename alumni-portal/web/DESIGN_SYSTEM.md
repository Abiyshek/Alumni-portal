# KV2 Alumni design system

A clean, professional school look: **white** surfaces, **KVS blue** for structure and actions, and **yellow** as the accent (active nav underline, date chips, the primary "Register" button, step numbers). Spacing is generous: sections are 80 px apart and cards have 32 px of padding.

All tokens are defined at the top of `app/globals.css`. Use the variables and avoid hard-coded colours.

## Brand

| Asset | File | Source |
|---|---|---|
| KVS logo | `public/brand/kv-logo.svg`, also `app/icon.svg` (favicon) | The school's official website header (no2pondicherry.kvs.ac.in, served from the gov.in S3WaaS CDN) |
| PM SHRI logo | `public/brand/pm-shri-logo.png` | The same header |
| Components | `components/Brand.js`: `<KvLogo>`, `<PmShriLogo>`, `<Brand>` | Logo plus the school name and "Alumni Association" |

Don't recolour, stretch or redraw the logos. Both belong to KVS and the Ministry of Education. Get the school's approval before this site goes public.

## Header

1. **Top strip** (blue-900): Ministry of Education line and a link to the official school site.
2. **Brand bar** (white): KVS logo, school name, PM SHRI logo, account menu.
3. **Nav bar** (blue-800, sticky): white links, with a yellow underline on the current page.

## Tokens

| Group | Tokens | Use |
|---|---|---|
| Blue | `--blue-900 … --blue-50` | Headings and footer (900), nav (800), buttons and links (700), tinted panels (100/50) |
| Yellow | `--yellow-500/600/100` | Accent: active nav, date chips, `.btn.accent`, step numbers, eyebrow underline |
| Text | `--ink`, `--text-2`, `--text-3` | Body / secondary / hints and metadata |
| Surfaces | `--surface`, `--surface-2`, `--line`, `--line-strong` | White cards, grey alternating sections, borders |
| Semantic | `--success --warning --danger --info` | Status tags, toasts, errors |
| Shadow | `--shadow-1/2/3` | Hairline / card / hover and menus |
| Radius | `--r-sm 8`, `--r-md 12`, `--r-lg 16`, `--r-pill` | Buttons and inputs / small panels / cards / chips |
| Spacing | `--s-1 … --s-9` (4 → 112 px) | All padding and gaps |
| Motion | `--ease`, `--dur-1/2` (150/250 ms) | Hovers, toasts, a short page fade-in. Turned off when the visitor prefers reduced motion. |
| Type | `--font-display` Plus Jakarta Sans, `--font-body` Inter | Headings and numbers / everything else |

## Components

| Class / component | Variants | States |
|---|---|---|
| `.glass` (white card) | add `.card`, `.interactive` | `.interactive` lifts 2 px on hover and deepens the shadow |
| `.btn` | default (blue), `.accent` (yellow), `.outline` / `.glass-btn`, `.ghost`, `.danger`, `.on` (RSVP'd) · sizes `.sm` `.lg` · `.block` | darker on hover, `:disabled` at 55% opacity, visible focus ring |
| `.tag` | `.saffron` (yellow), `.pending`, `.approved`, `.rejected`, `.suspended` | – |
| `.chip` | `.on` (blue) | filter tabs (jobs, admin) |
| Landing sections | `.section`, `.section.alt` (grey), `.bleed` (full width) | – |
| `<Field>` | text, email, password, number, url, datetime-local, `options` → select, `rows` → textarea | blue focus ring, `hint` text, required `*` |
| `<Avatar>` | `sm md lg xl` | photo, or initials on light blue |
| `<DateChip>` | `large` | – |
| `<Empty>` | icon + title + hint | Every empty list says what belongs there and how to add the first item |
| Toasts | `success`, `error` | Shown with `useToast()`, bottom right, close after 4 s |
| `<Protected level>` | `login`, `approved`, `admin` | Redirects to /login or /pending. Shows "Coordinators only" when access is denied. |

## Copy rules

- Buttons start with a verb and say what they do: "Create account", "Publish event", "Pin to the wall". Avoid "Submit" and "OK".
- Error messages say what happened and how to fix it: "That email and password don't match. Check them and try again."
- Confirmations name the item and the consequence: *Delete "Annual Alumni Meet"? This removes all RSVPs and can't be undone.*
- Use the same words everywhere: **alumni** (people), **batch of YYYY**, **coordinator** (an admin), **verified**.
