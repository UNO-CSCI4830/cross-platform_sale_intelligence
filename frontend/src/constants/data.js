// ── Theme Colors ─────────────────────────────────────────────────────────
export const COLORS = {
  bg: "#0f0f0f",
  sidebar: "#161616",
  card: "#1c1c1c",
  cardHover: "#222222",
  border: "#2a2a2a",
  accent: "#f0a500",
  accentDim: "#f0a50022",
  text: "#f0ede8",
  textMuted: "#7a7a7a",
  textDim: "#444",
  green: "#4caf7d",
  red: "#e05c5c",
  blue: "#5b9cf6",
};

// ── Platform accent colors ────────────────────────────────────────────────
export const PLATFORM_COLORS = {
  Poshmark: "#e8456a",
  Depop: "#ff4040",
  Mercari: "#00a0e9",
  eBay: "#f5a623",
};

// ── Dropdown options ──────────────────────────────────────────────────────
export const PLATFORMS = ["All Platforms", "Poshmark", "Depop", "Mercari", "eBay"];
export const CONDITIONS = ["New with Tags", "Like New", "Good", "Fair", "Poor"];
export const CATEGORIES = ["Apparel", "Electronics", "Home & Garden", "Collectibles & Toys", "Handmade", "Other"];

// ── Shipping weight tiers (lbs → estimated cost USD) ─────────────────────
export const SHIPPING_RATES = [
  { maxLbs: 0.5,  label: "Under 0.5 lb",   usps: 4.50,  ups: 8.50  },
  { maxLbs: 1,    label: "0.5 – 1 lb",     usps: 5.25,  ups: 9.00  },
  { maxLbs: 2,    label: "1 – 2 lbs",      usps: 7.00,  ups: 10.50 },
  { maxLbs: 5,    label: "2 – 5 lbs",      usps: 10.50, ups: 13.00 },
  { maxLbs: 10,   label: "5 – 10 lbs",     usps: 15.00, ups: 17.50 },
  { maxLbs: 20,   label: "10 – 20 lbs",    usps: 22.00, ups: 24.00 },
  { maxLbs: 9999, label: "Over 20 lbs",    usps: 35.00, ups: 38.00 },
];

export function estimateShipping(weightLbs) {
  if (!weightLbs || weightLbs <= 0) return null;
  const tier = SHIPPING_RATES.find((t) => weightLbs <= t.maxLbs);
  return tier ?? SHIPPING_RATES[SHIPPING_RATES.length - 1];
}

// ── Demo listings ──────────────────────────────────────────────────
export const LISTINGS = [

];
