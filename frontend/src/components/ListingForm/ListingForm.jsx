import { useState } from "react";
import "./ListingForm.css";
import { PLATFORMS, CONDITIONS, CATEGORIES } from "../../constants/data";

// ── AddListingForm ────────────────────────────────────────────────────────
// Modal form for adding a new listing.
// Props:
//   onAdd   — callback(listing) called with the new listing object on submit
//   onClose — callback() called when the modal should close
export function AddListingForm({ onAdd, onClose }) {
  const [form, setForm] = useState({
    platform:  "Poshmark",
    title:     "",
    category:  "Tops",
    size:      "",
    condition: "Good",
    price:     "",
    notes:     "",
    stains:    false,
    damage:    false,
    fading:    false,
  });

  // Generic change handler for text/select inputs
  const handleChange = (key) => (e) =>
    setForm((prev) => ({ ...prev, [key]: e.target.value }));

  // Generic change handler for checkboxes
  const handleCheck = (key) => (e) =>
    setForm((prev) => ({ ...prev, [key]: e.target.checked }));

  const handleSubmit = () => {
    if (!form.title.trim() || !form.price) return; // basic validation
    onAdd({ ...form, id: Date.now(), price: parseFloat(form.price) });
    onClose();
  };

  // Reusable field renderer
  const Field = ({ label, fieldKey, type = "text", options = null }) => (
    <div className="form-field">
      <label>{label}</label>
      {options ? (
        <select value={form[fieldKey]} onChange={handleChange(fieldKey)}>
          {options.map((o) => <option key={o}>{o}</option>)}
        </select>
      ) : (
        <input
          type={type}
          value={form[fieldKey]}
          onChange={handleChange(fieldKey)}
        />
      )}
    </div>
  );

  return (
    <div className="form-overlay">
      <div className="form-panel">

        {/* Header */}
        <div className="form-panel__header">
          <h3 className="form-panel__title">New Listing</h3>
          <button className="form-panel__close" onClick={onClose}>✕</button>
        </div>

        {/* Form fields */}
        <div className="form-grid">
          <Field label="Platform"    fieldKey="platform"  options={PLATFORMS.slice(1)} />
          <Field label="Category"    fieldKey="category"  options={CATEGORIES} />
          <div className="form-grid--full">
            <Field label="Title" fieldKey="title" />
          </div>
          <Field label="Size"        fieldKey="size" />
          <Field label="Condition"   fieldKey="condition" options={CONDITIONS} />
          <Field label="Price ($)"   fieldKey="price"     type="number" />

          {/* Notes — full width, textarea */}
          <div className="form-field form-grid--full">
            <label>Notes</label>
            <textarea
              value={form.notes}
              onChange={handleChange("notes")}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="form-actions">
          <button className="btn-primary"   onClick={handleSubmit}>Add Listing</button>
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
        </div>

      </div>
    </div>
  );
}
