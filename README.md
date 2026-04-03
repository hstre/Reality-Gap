# Reality Gap (RG) — Research Website

A static public website for the **Reality Gap (RG)** research project.

Reality Gap is a heuristic indicator measuring whether a company's market capitalisation is approximately covered by its estimated fundamental base (derived from smoothed earnings and tangible equity). This site presents the methodology, working paper, and an initial set of illustrative company data.

**Live site:** https://hstre.github.io/reality-gap/

---

## Technical Stack

| Component | Choice |
|-----------|--------|
| Framework | [Astro](https://astro.build/) v4 (static output) |
| Styling | [Tailwind CSS](https://tailwindcss.com/) v3 |
| Language | TypeScript |
| Data | Local JSON files |
| Hosting | GitHub Pages |
| i18n | Manual (English + German) |

No backend. No database. No authentication. No live API calls.

---

## Local Setup

### Prerequisites

- Node.js 18 or higher
- npm

### Install

```bash
git clone https://github.com/hstre/reality-gap.git
cd reality-gap
npm install
```

### Start Development Server

```bash
npm run dev
```

Opens at http://localhost:4321/reality-gap/

### Production Build

```bash
npm run build
```

Output is written to `./dist/`.

### Preview Production Build

```bash
npm run preview
```

---

## GitHub Pages Deployment

### Automatic (recommended)

The repository includes a GitHub Actions workflow at `.github/workflows/deploy.yml`.

**Setup steps:**

1. Push the repository to GitHub (repo name: `reality-gap`, owner: `hstre`)
2. Go to **Settings → Pages** in the GitHub repository
3. Under **Source**, select **GitHub Actions**
4. Push a commit to `main` — the workflow builds and deploys automatically

The site will be available at: `https://hstre.github.io/reality-gap/`

### Manual Deployment

```bash
npm run build
# Then upload the ./dist/ folder to your hosting provider
```

---

## Project Structure

```
src/
├── components/
│   ├── layout/
│   │   ├── BaseLayout.astro   # HTML head, global layout
│   │   ├── Header.astro       # Navigation + language switcher
│   │   └── Footer.astro       # Footer
│   ├── ui/
│   │   ├── CompanyCard.astro  # Card for company overview
│   │   ├── MetricBlock.astro  # Single RG metric display block
│   │   └── TrendBadge.astro   # Trend code badge (++, +, =, -, --)
│   └── RankingTable.astro     # Sortable rankings table (with JS)
├── data/
│   ├── companies/
│   │   ├── tesla.json
│   │   ├── apple.json
│   │   ├── nvidia.json
│   │   ├── microsoft.json
│   │   └── samsung.json
│   ├── companies.index.json   # List of company slugs
│   └── sectors.json           # List of sectors (for filter)
├── i18n/
│   ├── en.ts                  # English translations
│   └── de.ts                  # German translations
├── lib/
│   ├── rg.ts                  # Core types + utility functions
│   ├── format.ts              # Number/currency formatters
│   └── sort.ts                # Sort helpers
├── pages/
│   ├── index.astro            # Home (EN)
│   ├── methodology.astro      # Methodology (EN)
│   ├── paper.astro            # Paper (EN)
│   ├── companies/
│   │   ├── index.astro        # Companies overview (EN)
│   │   └── [slug].astro       # Company detail page (EN)
│   ├── rankings.astro         # Rankings (EN)
│   ├── about.astro            # About (EN)
│   └── de/                    # German equivalents
│       ├── index.astro
│       ├── methodik.astro
│       ├── paper.astro
│       ├── unternehmen/
│       │   ├── index.astro
│       │   └── [slug].astro
│       ├── rankings.astro
│       └── ueber.astro
└── styles/
    ├── global.css             # Tailwind imports + custom layers
    └── tokens.css             # CSS custom properties (colors, fonts)

public/
├── favicon.svg
└── papers/
    └── reality-gap-working-paper.pdf   ← place PDF here
```

---

## Data Structure

Each company is stored in its own JSON file under `src/data/companies/`.

### Company Schema

```json
{
  "company": "Tesla",
  "ticker": "TSLA",
  "slug": "tesla",
  "sector": "Automotive / Technology",
  "currency": "USD",
  "description": "Illustrative approximation in the initial public RG dataset.",
  "observations": [
    {
      "periodKey": "2026_q1",
      "periodLabel": "Q1 2026",
      "rg8": 12.4,
      "rg10": 11.3,
      "rg12": 10.5,
      "trend": "-",
      "marketCap": 1353,
      "bookEquity": 82,
      "netIncome": 3.8,
      "fundamentalBaseApprox": 120,
      "note": "Illustrative approximation, not fully adjusted."
    }
  ]
}
```

**Field reference:**

| Field | Type | Description |
|-------|------|-------------|
| `company` | string | Display name |
| `ticker` | string | Exchange ticker symbol |
| `slug` | string | URL-safe identifier (lowercase, no spaces) |
| `sector` | string | Sector label (must match `sectors.json`) |
| `currency` | string | ISO 4217 currency code |
| `description` | string | Optional short description |
| `observations` | array | List of quarterly observations |

**Observation fields:**

| Field | Type | Description |
|-------|------|-------------|
| `periodKey` | string | Internal key, e.g. `"2026_q1"` |
| `periodLabel` | string | Display label, e.g. `"Q1 2026"` |
| `rg8` | number | RG value using 8-quarter smoothing |
| `rg10` | number | RG value using 10-quarter smoothing |
| `rg12` | number | RG value using 12-quarter smoothing |
| `trend` | string | One of: `++`, `+`, `=`, `-`, `--` |
| `marketCap` | number? | Market cap in billions |
| `bookEquity` | number? | Book equity in billions |
| `netIncome` | number? | Net income in billions (annualised) |
| `fundamentalBaseApprox` | number? | Estimated fundamental base in billions |
| `note` | string? | Data quality or disclaimer note |

### Period Key Format

Internal period keys use the format `YYYY_qN`:

```
2026_q1  →  Q1 2026
2026_q2  →  Q2 2026
2025_q4  →  Q4 2025
```

The site automatically determines the **latest observation** by sorting on `periodKey`. Do not hardcode which quarter is "current".

---

## How to Add a New Company

1. Create `src/data/companies/<slug>.json` following the schema above
2. Add the slug to `src/data/companies.index.json`
3. If the sector is new, add it to `src/data/sectors.json`
4. Run `npm run build` to verify

Example — adding Alphabet:

```json
// src/data/companies/alphabet.json
{
  "company": "Alphabet",
  "ticker": "GOOGL",
  "slug": "alphabet",
  "sector": "Technology",
  "currency": "USD",
  "description": "Illustrative approximation.",
  "observations": [
    {
      "periodKey": "2026_q1",
      "periodLabel": "Q1 2026",
      "rg8": 22.1,
      "rg10": 21.4,
      "rg12": 20.8,
      "trend": "+",
      "note": "Illustrative approximation."
    }
  ]
}
```

Then add `"alphabet"` to `companies.index.json`:

```json
["tesla", "apple", "nvidia", "microsoft", "samsung", "alphabet"]
```

---

## How to Add a New Quarter

In the relevant company JSON file, prepend a new observation to the `observations` array:

```json
"observations": [
  {
    "periodKey": "2026_q2",
    "periodLabel": "Q2 2026",
    "rg8": 11.9,
    "rg10": 10.8,
    "rg12": 10.1,
    "trend": "=",
    "marketCap": 1410,
    "bookEquity": 85,
    "netIncome": 3.9,
    "fundamentalBaseApprox": 122,
    "note": "Illustrative approximation."
  },
  {
    "periodKey": "2026_q1",
    ...
  }
]
```

The site will automatically display the latest observation (determined by `periodKey` sort order).

---

## How to Add the Paper PDF

Place the PDF file at:

```
public/papers/reality-gap-working-paper.pdf
```

The paper page links to this file automatically. Do not change the filename unless you also update the path in `src/pages/paper.astro` and `src/pages/de/paper.astro`.

---

## Language Support

The site supports **English** (default) and **German**.

| English URL | German URL |
|-------------|------------|
| `/` | `/de/` |
| `/methodology` | `/de/methodik` |
| `/paper` | `/de/paper` |
| `/companies` | `/de/unternehmen` |
| `/companies/tesla` | `/de/unternehmen/tesla` |
| `/rankings` | `/de/rankings` |
| `/about` | `/de/ueber` |

Translations are in `src/i18n/en.ts` and `src/i18n/de.ts`. To add a new language, create a new translation file and add pages under a new language directory.

---

## Configuration

Key configuration file: `astro.config.mjs`

```js
export default defineConfig({
  integrations: [tailwind()],
  output: 'static',
  site: 'https://hstre.github.io',
  base: '/reality-gap',
});
```

- `site`: Full site URL (used for canonical URLs and OG tags)
- `base`: Base path for GitHub Pages deployment

If you deploy to a custom domain (e.g. `reality-gap.com`), update both `site` and `base` (set `base: '/'`).

---

## Design Principles

- Light, white background — no dark mode
- Academic typography (Georgia for headings, system-ui for body)
- Single accent color: `#3b6e9e` (muted blue)
- No animations, no gradients, no decorative elements
- Generous whitespace
- Responsive at all screen sizes

---

## Future Extension Points

The architecture is designed to support these additions without restructuring:

- **More companies**: add JSON files + update index
- **More quarters**: add observations to existing company files
- **Historical charts**: add a chart library (e.g. Chart.js) to company detail pages — the data model is already structured for time series
- **Quarter selector**: add a dropdown on detail pages to switch between observations
- **Status badges**: add `dataStatus`, `isApproximation` etc. fields to observations
- **CSV/JSON export**: generate export files during build from existing JSON data
- **Semi-automated data updates**: write a script to update JSON files from a data source

---

## License

Research project. All data is illustrative. Not investment advice.
