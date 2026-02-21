import { useState } from "react";
import "./ListingForm.css";
import { PLATFORMS, CONDITIONS, CATEGORIES } from "../../constants/data";

// ── Field ────────────────────────────────────────────────────────
function Field({ label, fieldKey, value, onChange, type = "text", options = null }) {
  return (
    <div className="form-field">
      <label>{label}</label>
      {options ? (
        <select value={value} onChange={(e) => onChange(fieldKey, e.target.value)}>
          {options.map((o) => <option key={o}>{o}</option>)}
        </select>
      ) : (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(fieldKey, e.target.value)}
        />
      )}
    </div>
  );
}

// ── AddListingForm ────────────────────────────────────────────────────────
// Modal form for adding a new listing.
// Props:
//   onAdd   — callback(listing) called with the new listing object on submit
//   onClose — callback() called when the modal should close 
//   onDelete   — optional callback(id) called when the listing is deleted
//   initial    — optional existing listing object (triggers "edit" mode)
export function AddListingForm({ onAdd, onClose, onDelete, initial }) {
  const isEditing = !!initial;

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

  const handleChange = (key, value) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = () => {
    if (!form.title.trim() || !form.price) return;
    onAdd({
      ...form,
      id:    isEditing ? form.id : Date.now(),
      price: parseFloat(form.price),
    });
    onClose();
  };

  const handleDelete = () => {
    if (onDelete) onDelete(form.id);
    onClose();
  };

  return (
    <div className="form-overlay">
      <div className="form-panel">

        {/* Header */}
        <div className="form-panel__header">
          <h3 className="form-panel__title">{isEditing ? "Edit Listing" : "New Listing"}</h3>
          <button className="form-panel__close" onClick={onClose}>✕</button>
        </div>

        {/* Form fields */}
        <div className="form-grid">
          <Field label="Platform"  fieldKey="platform"  value={form.platform}  onChange={handleChange} options={PLATFORMS.slice(1)} />
          <Field label="Category"  fieldKey="category"  value={form.category}  onChange={handleChange} options={CATEGORIES} />
          <div className="form-grid--full">
            <Field label="Title"   fieldKey="title"     value={form.title}     onChange={handleChange} />
          </div>
          <Field label="Size"      fieldKey="size"      value={form.size}      onChange={handleChange} />
          <Field label="Condition" fieldKey="condition" value={form.condition} onChange={handleChange} options={CONDITIONS} />
          <Field label="Price ($)" fieldKey="price"     value={form.price}     onChange={handleChange} type="number" />

          {/* Notes — full width, textarea */}
          <div className="form-field form-grid--full">
            <label>Notes</label>
            <textarea
              value={form.notes}
              onChange={(e) => handleChange("notes", e.target.value)}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="form-actions">
          <button className="btn-primary" onClick={handleSubmit}>
            {isEditing ? "Save Changes" : "Add Listing"}
          </button>
          {isEditing && (
            <button className="btn-danger" onClick={handleDelete}>Delete</button>
          )}
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
        </div>

      </div>
    </div>
  );
}
