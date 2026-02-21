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
//   editingListing — listing object being edited, or null
export default function Dashboard() {
  const [listings,        setListings]        = useState(LISTINGS);
  const [activePlatform,  setActivePlatform]  = useState("All Platforms");
  const [showForm,        setShowForm]        = useState(false);
  const [editingListing,  setEditingListing]  = useState(null);

  // ── Derived values ────────────────────────────────────────────────────
  const filtered = activePlatform === "All Platforms"
    ? listings
    : listings.filter((l) => l.platform === activePlatform);

  const totalValue = filtered.reduce((sum, l) => sum + l.price, 0);
  const avgPrice   = filtered.length
    ? (totalValue / filtered.length).toFixed(2)
    : "0.00";

  // ── Handlers ──────────────────────────────────────────────────────────
  // Add a brand-new listing
  const handleAddListing = (newListing) =>
    setListings((prev) => [newListing, ...prev]);

  // Save edits to an existing listing
  const handleSaveListing = (updated) =>
    setListings((prev) => prev.map((l) => (l.id === updated.id ? updated : l)));

  // Delete a listing by id
  const handleDeleteListing = (id) =>
    setListings((prev) => prev.filter((l) => l.id !== id));

  // ── Render ────────────────────────────────────────────────────────────
  return (
    <div className="dashboard">

      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar__brand">
          <p className="sidebar__brand-name">Cross-Platform Resale Intelligence</p>
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

        {/* ── To be edited later ── */}
        <div className="sidebar__footer">
          <p>Logged in as User</p>
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
        </div>

        {/* Listings */}
        {filtered.length === 0 ? (
          <div className="empty-state">
            No listings yet. Click "+ Add Listing" to get started.
          </div>
        ) : (
          <div className="listings-grid">
            {filtered.map((l) => (
              <GridCard
                key={l.id}
                listing={l}
                onClick={() => setEditingListing(l)}
              />
            ))}
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

      {/* Edit Listing modal */}
      {editingListing && (
        <AddListingForm
          initial={editingListing}
          onAdd={handleSaveListing}
          onDelete={handleDeleteListing}
          onClose={() => setEditingListing(null)}
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
