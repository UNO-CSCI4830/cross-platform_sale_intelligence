import { useState, useEffect, useCallback } from "react";
import "./Dashboard.css";
import { GridCard } from "../ListingCard/ListingCard";
import { AddListingForm } from "../ListingForm/ListingForm";
import { COLORS, PLATFORMS} from "../../constants/data";

const API_BASE = "http://localhost:8000";

// ── Dashboard ─────────────────────────────────────────────────────────────
// Top-level component. Owns all app state:
// user — logged-in user's email (string)
// userId — logged-in user's id (int)
// token — JWT access token (string)
// onLogout — callback to clear session and return to login
export default function Dashboard({ user, userId, token, onLogout }) {
  const [listings, setListings] = useState([]);
  const [activePlatform, setActivePlatform] = useState("All Platforms");
  const [showForm, setShowForm] = useState(false);
  const [editingListing, setEditingListing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showProfile, setShowProfile] = useState(false);

  const authHeaders = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
  };

  // ── Fetch listing ──────────────────────────────────────────────────────
  const fetchListings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/listings/${userId}`, {
        headers: authHeaders,
      });
      if (!res.ok) throw new Error("Failed to load listings.");
      const data = await res.json();
      setListings(data.map(normalise));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [userId, token]);
 
  useEffect(() => {
    fetchListings();
  }, [fetchListings]);

  // ── Derived values ────────────────────────────────────────────────────
  const filtered = activePlatform === "All Platforms"
    ? listings
    : listings.filter((l) => l.platform === activePlatform);

  const totalValue = filtered.reduce((sum, l) => sum + l.price, 0);
  const avgPrice = filtered.length
    ? (totalValue / filtered.length).toFixed(2)
    : "0.00";

  // ── Handlers ──────────────────────────────────────────────────────────
  // Add a brand-new listing
    const handleAddListing = async (newListing) => {
    try {
      const res = await fetch(`${API_BASE}/listings`, {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify(serialise(newListing, userId)),
      });
      if (!res.ok) throw new Error("Failed to add listing.");
      const saved = await res.json();
      setListings((prev) => [normalise(saved), ...prev]);
    } catch (err) {
      alert("Error adding listing: " + err.message);
    }
  };
 
  const handleSaveListing = async (updated) => {
    try {
      const res = await fetch(`${API_BASE}/listings/${updated.id}`, {
        method: "PUT",
        headers: authHeaders,
        body: JSON.stringify(serialise(updated, userId)),
      });
      if (!res.ok) throw new Error("Failed to update listing.");
      const saved = await res.json();
      setListings((prev) => prev.map((l) => (l.id === saved.id ? normalise(saved) : l)));
    } catch (err) {
      alert("Error updating listing: " + err.message);
    }
  };
 
  const handleDeleteListing = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/listings/${id}`, {
        method: "DELETE",
        headers: authHeaders,
      });
      if (!res.ok) throw new Error("Failed to delete listing.");
      setListings((prev) => prev.filter((l) => l.id !== id));
    } catch (err) {
      alert("Error deleting listing: " + err.message);
    }
  };

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

        <div className="sidebar__footer">
          <p title={user}>{user}</p>
          <p>v0.1 · Baseline Build</p>

          <button className="sidebar__profile" onClick={() => setShowProfile(true)}>
            ✎ Edit Profile
          </button>

          <a
            href="https://forms.gle/uJjbzj26iHBpLDad9"
            target="_blank"
            rel="noreferrer"
            className="sidebar__logout"
            style={{ display: "inline-block", marginBottom: "6px", textDecoration: "none" }}
          >
            ⚐ Report a Bug
          </a>
          {onLogout && (
            <button className="sidebar__logout" onClick={onLogout}>
              Log out
            </button>
          )}
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
          <StatCard label="Total Listings" value={filtered.length}  color={COLORS.text}   />
          <StatCard label="Total Value" value={`$${totalValue.toFixed(2)}`} color={COLORS.accent} />
          <StatCard label="Avg Price" value={`$${avgPrice}`}  color={COLORS.text}   />
        </div>

        {/* Listings */}
        {loading ? (
          <div className="empty-state">Loading your listings…</div>
        ) : error ? (
          <div className="empty-state" style={{ color: "#e05c5c" }}>
            {error}&nbsp;
            <button
              onClick={fetchListings}
              style={{ cursor: "pointer", color: "#f0a500", background: "none", border: "none", fontFamily: "inherit" }}
            >
              Retry
            </button>
          </div>
        ) : filtered.length === 0 ? (
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

      {/* Profile modal */}
      {showProfile && (
        <ProfileForm
          userId={userId}
          currentEmail={user}
          token={token}
          onClose={() => setShowProfile(false)}
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

// ── ProfileForm ───────────────────────────────────────────────────────────
function ProfileForm({ userId, currentEmail, token, onClose }) {
  const [email,   setEmail]   = useState(currentEmail);
  const [error,   setError]   = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
 
  const handleSave = async () => {
    setError(""); setSuccess("");
    if (!email.trim()) { setError("Email cannot be empty."); return; }
 
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/users/${userId}`, {
        method:  "PUT",
        headers: {
          "Content-Type":  "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || "Update failed."); return; }
      setSuccess("Email updated! Changes will show after next login.");
    } catch {
      setError("Could not reach the server.");
    } finally {
      setLoading(false);
    }
  };
 
  return (
    <div className="form-overlay">
      <div className="form-panel" style={{ width: 360 }}>
        <div className="form-panel__header">
          <h3 className="form-panel__title">Edit Profile</h3>
          <button className="form-panel__close" onClick={onClose}>✕</button>
        </div>
 
        <div className="form-field">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSave()}
          />
        </div>
 
        {error   && <p style={{ color: "#e05c5c", fontSize: 12, marginTop: 8 }}>{error}</p>}
        {success && <p style={{ color: "#4caf7d", fontSize: 12, marginTop: 8 }}>{success}</p>}
 
        <div className="form-actions" style={{ marginTop: 16 }}>
          <button className="btn-primary" onClick={handleSave} disabled={loading}>
            {loading ? "Saving…" : "Save Changes"}
          </button>
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
        </div>
      </div>
    </div>
  );
}

// ── Shape helpers ─────────────────────────────────────────────────────────
// Convert backend response to frontend listing shape
function normalise(l) {
  return {
    id:        l.id,
    title:     l.title,
    price:     l.price,
    condition: l.condition,
    platform:  l.platform,
    category:  l.category   ?? "Other",
    size:      l.size       ?? "",
    notes:     l.notes      ?? "",
    weightLbs: l.weight_lbs ?? null,
    imageUrl:  l.image_url  ?? "",
    status:    l.status     ?? "active",
  };
}
 
// Convert frontend listing shape to backend request body
function serialise(l, userId) {
  return {
    user_id:    userId,
    title:      l.title,
    price:      parseFloat(l.price),
    condition:  l.condition,
    platform:   l.platform,
    category:   l.category,
    size:       l.size,
    notes:      l.notes,
    weight_lbs: l.weightLbs ? parseFloat(l.weightLbs) : null,
    image_url:  l.imageUrl  || null,
    status:     l.status    ?? "active",
  };
}