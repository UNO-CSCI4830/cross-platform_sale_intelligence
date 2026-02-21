import { useState } from "react";
import "./Dashboard.css";
import { GridCard } from "../ListingCard/ListingCard";
import { AddListingForm } from "../ListingForm/ListingForm";
import { COLORS, PLATFORMS, LISTINGS } from "../../constants/data";

// ── Dashboard ─────────────────────────────────────────────────────────────
// Top-level component. Owns all app state:
//   listings       — array of listing objects
//   activePlatform — currently selected sidebar filter
//   showForm       — boolean, whether the Add Listing modal is open
export default function Dashboard() {
  const [listings,        setListings]        = useState(LISTINGS);
  const [activePlatform,  setActivePlatform]  = useState("All Platforms");
  const [showForm,        setShowForm]        = useState(false);

  // ── Derived values ────────────────────────────────────────────────────
  const filtered = activePlatform === "All Platforms"
    ? listings
    : listings.filter((l) => l.platform === activePlatform);

  const totalValue = filtered.reduce((sum, l) => sum + l.price, 0);
  const flagged    = filtered.filter((l) => l.stains || l.damage || l.fading).length;
  const avgPrice   = filtered.length
    ? (totalValue / filtered.length).toFixed(2)
    : "0.00";

  // ── Handlers ──────────────────────────────────────────────────────────
  const handleAddListing = (newListing) =>
    setListings((prev) => [newListing, ...prev]);

  // ── Render ────────────────────────────────────────────────────────────
  return (
    <div className="dashboard">

      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar__brand">
          <p className="sidebar__brand-name">ResaleIQ</p>
          <p className="sidebar__brand-sub">Multi-Platform Dashboard</p>
        </div>

        <p className="sidebar__section-label">Platforms</p>

        {PLATFORMS.map((p) => {
          const count = p === "All Platforms"
            ? listings.length
            : listings.filter((l) => l.platform === p).length;

          return (
            <div
              key={p}
              className={`sidebar__item ${activePlatform === p ? "sidebar__item--active" : ""}`}
              onClick={() => setActivePlatform(p)}
            >
              <span>{p}</span>
              <span className="sidebar__item-count">{count}</span>
            </div>
          );
        })}

        <div className="sidebar__footer">
          <p>Logged in as Emily</p>
          <p>v0.1 · Baseline Build</p>
        </div>
      </aside>

      {/* ── Main content ── */}
      <main className="main">

        {/* Header */}
        <div className="main__header">
          <div>
            <h1 className="main__title">{activePlatform}</h1>
            <p className="main__subtitle">
              {filtered.length} listing{filtered.length !== 1 ? "s" : ""}
            </p>
          </div>

          <div className="main__actions">
            <button className="btn-add" onClick={() => setShowForm(true)}>
              + Add Listing
            </button>
          </div>
        </div>

        {/* Stats bar */}
        <div className="stats-bar">
          <StatCard label="Total Listings" value={filtered.length}             color={COLORS.text}   />
          <StatCard label="Total Value"    value={`$${totalValue.toFixed(2)}`} color={COLORS.accent} />
          <StatCard label="Avg Price"      value={`$${avgPrice}`}              color={COLORS.text}   />
          <StatCard label="Flagged Items"  value={flagged}                     color={flagged > 0 ? COLORS.red : COLORS.green} />
        </div>

        {/* Listings */}
        {filtered.length === 0 ? (
          <div className="empty-state">
            No listings yet. Click "+ Add Listing" to get started.
          </div>
        ) : (
          <div className="listings-grid">
            {filtered.map((l) => <GridCard key={l.id} listing={l} />)}
          </div>
        )}
      </main>

      {/* Add Listing modal */}
      {showForm && (
        <AddListingForm
          onAdd={handleAddListing}
          onClose={() => setShowForm(false)}
        />
      )}
    </div>
  );
}

// ── StatCard (local helper) ───────────────────────────────────────────────
// Small stat display used only inside Dashboard.
function StatCard({ label, value, color }) {
  return (
    <div className="stat-card">
      <p className="stat-card__label">{label}</p>
      <p className="stat-card__value" style={{ color }}>{value}</p>
    </div>
  );
}
