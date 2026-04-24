// hooks/useComps.js
// Reads resale_dashboard.json and returns pricing + condition comps for a given search term.
// Usage: const { comps, suggestion, conditionSuggestion } = useComps(searchTerm);

import { useMemo } from "react";
import dashboardData from "../data/resale_dashboard.json";

// Parse the newline-delimited JSON file into an array.
// resale_dashboard.json is exported as one JSON object per line (NDJSON).
// If your bundler imports it as a plain string, split on newlines and parse each line.
// If your bundler (Vite/CRA) parses it as an array already, this still works.
function parseRecords(raw) {
  if (Array.isArray(raw)) return raw;
  if (typeof raw === "object") return [raw]; // single object edge-case
  // NDJSON string fallback
  return String(raw)
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean)
    .map((l) => JSON.parse(l));
}

const ALL_RECORDS = parseRecords(dashboardData);

// Score a record's keywords against the user's search term.
// Returns a number 0–1 (1 = exact match).
function score(recordKeywords, term) {
  const a = recordKeywords.toLowerCase();
  const b = term.toLowerCase();
  if (a === b) return 1;
  if (a.includes(b) || b.includes(a)) return 0.8;
  // Token overlap
  const tokA = new Set(a.split(/\s+/));
  const tokB = b.split(/\s+/);
  const overlap = tokB.filter((t) => tokA.has(t)).length;
  return overlap / Math.max(tokA.size, tokB.length);
}

// Tally condition values across a set of comp records and return the most common one.
// Returns null if no records have a condition field.
function getMostCommonCondition(records) {
  const tally = {};
  for (const rec of records) {
    if (!rec.condition) continue;
    tally[rec.condition] = (tally[rec.condition] ?? 0) + 1;
  }
  const entries = Object.entries(tally);
  if (!entries.length) return null;

  // Sort descending by count and pick the winner
  entries.sort((a, b) => b[1] - a[1]);
  const [topCondition, topCount] = entries[0];

  return {
    condition:   topCondition,           // e.g. "Used"
    count:       topCount,               // how many comps had this condition
    total:       records.length,         // total comps in the bucket
    percentage:  Math.round((topCount / records.length) * 100),
    // All conditions with their counts, for optional display
    breakdown:   Object.fromEntries(entries),
  };
}

export function useComps(searchTerm) {
  return useMemo(() => {
    const term = (searchTerm || "").trim();
    if (!term) return { comps: [], suggestion: null, conditionSuggestion: null };

    // Group all records by keyword bucket, pick the best-matching bucket
    const buckets = {};
    for (const rec of ALL_RECORDS) {
      const s = score(rec.keywords, term);
      if (s > 0) {
        if (!buckets[rec.keywords]) buckets[rec.keywords] = { s, records: [] };
        if (s > buckets[rec.keywords].s) buckets[rec.keywords].s = s;
        buckets[rec.keywords].records.push(rec);
      }
    }

    const best = Object.values(buckets).sort((a, b) => b.s - a.s)[0];
    if (!best || best.s < 0.3) return { comps: [], suggestion: null, conditionSuggestion: null };

    const comps = best.records;

    // Use the pre-calculated avg/suggested values from the first record
    // (they're identical within a keyword group)
    const { avg_price, suggested_listing_price } = comps[0];

    return {
      comps,                    // array of matching listing records
      suggestion: {
        avgPrice:        avg_price,
        suggestedPrice:  suggested_listing_price,
        sampleSize:      comps.length,
        keywords:        comps[0].keywords,
      },
      conditionSuggestion: getMostCommonCondition(comps),
    };
  }, [searchTerm]);
}