import { useState, useRef } from "react";
import "./ListingForm.css";
import { PLATFORMS, CONDITIONS, CATEGORIES, estimateShipping } from "../../constants/data";
import { useComps } from "../../hooks/useComps";

// ── Field ─────────────────────────────────────────────────────────────────────
function Field({ label, fieldKey, value, onChange, type = "text", options = null, placeholder = "" }) {
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
          placeholder={placeholder}
          onChange={(e) => onChange(fieldKey, e.target.value)}
        />
      )}
    </div>
  );
}

// ── ImageUpload ───────────────────────────────────────────────────────────────
function ImageUpload({ value, onChange }) {
  const inputRef = useRef(null);

  const readFile = (file) => {
    if (!file || !file.type.startsWith("image/")) return;
    const reader = new FileReader();
    reader.onload = (e) => onChange("imageUrl", e.target.result);
    reader.readAsDataURL(file);
  };

  return (
    <div className="form-image-section">
      <div className="image-upload" onClick={() => inputRef.current.click()}>
        {value ? (
          <img src={value} alt="listing" className="image-upload__preview" />
        ) : (
          <div className="image-upload__placeholder">
            <span className="image-upload__icon">+</span>
            <span className="image-upload__hint">Click to upload a photo</span>
            <span className="image-upload__sub">JPG · PNG · WEBP</span>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          style={{ display: "none" }}
          onChange={(e) => readFile(e.target.files[0])}
        />
      </div>
      {value && (
        <button className="image-upload__remove" onClick={() => onChange("imageUrl", "")}>
          Remove photo
        </button>
      )}
    </div>
  );
}

// ── ShippingEstimate ──────────────────────────────────────────────────────────
function ShippingEstimate({ weightLbs }) {
  const parsed = parseFloat(weightLbs);
  const tier = estimateShipping(parsed);

  if (!tier) {
    return (
      <div className="shipping-estimate shipping-estimate--empty">
        <span className="shipping-estimate__label">Est. Shipping</span>
        <span className="shipping-estimate__empty-hint">Enter weight above</span>
      </div>
    );
  }

  return (
    <div className="shipping-estimate">
      <span className="shipping-estimate__label">Est. Shipping</span>
      <div className="shipping-estimate__rates">
        <span className="shipping-estimate__carrier">
          USPS <strong>${tier.usps.toFixed(2)}</strong>
        </span>
        <span className="shipping-estimate__divider">·</span>
        <span className="shipping-estimate__carrier">
          UPS <strong>${tier.ups.toFixed(2)}</strong>
        </span>
      </div>
      <span className="shipping-estimate__tier">{tier.label}</span>
    </div>
  );
}

// ── CompsSuggestion ───────────────────────────────────────────────────────────
// Shown below the Title field when comps are found.
// "Use this price" pre-fills the Price field.
function CompsSuggestion({ suggestion, onUsePrice }) {
  if (!suggestion) return null;

  return (
    <div className="comps-suggestion">
      <div className="comps-suggestion__header">
        <span className="comps-suggestion__label">📊 eBay Comps</span>
        <span className="comps-suggestion__meta">
          {suggestion.sampleSize} listing{suggestion.sampleSize !== 1 ? "s" : ""} · "{suggestion.keywords}"
        </span>
      </div>
      <div className="comps-suggestion__prices">
        <div className="comps-suggestion__stat">
          <span className="comps-suggestion__stat-label">Avg sold</span>
          <span className="comps-suggestion__stat-value">${suggestion.avgPrice.toFixed(2)}</span>
        </div>
        <div className="comps-suggestion__divider" />
        <div className="comps-suggestion__stat">
          <span className="comps-suggestion__stat-label">Suggested list</span>
          <span className="comps-suggestion__stat-value comps-suggestion__stat-value--accent">
            ${suggestion.suggestedPrice.toFixed(2)}
          </span>
        </div>
        <button
          className="comps-suggestion__use-btn"
          onClick={() => onUsePrice(suggestion.suggestedPrice)}
          type="button"
        >
          Use this price
        </button>
      </div>
    </div>
  );
}

// ── ConditionSuggestion ───────────────────────────────────────────────────────
// Shown below the Condition dropdown when comps are found.
// Displays the most common condition across matching listings with a confidence
// percentage, and offers a "Use this condition" button to pre-fill the field.
function ConditionSuggestion({ conditionSuggestion, onUseCondition }) {
  if (!conditionSuggestion) return null;

  const { condition, percentage, count, total } = conditionSuggestion;

  return (
    <div className="comps-suggestion">
      <div className="comps-suggestion__header">
        <span className="comps-suggestion__label">🏷️ Condition Comps</span>
        <span className="comps-suggestion__meta">
          {count} of {total} listing{total !== 1 ? "s" : ""}
        </span>
      </div>
      <div className="comps-suggestion__prices">
        <div className="comps-suggestion__stat">
          <span className="comps-suggestion__stat-label">Most common</span>
          <span className="comps-suggestion__stat-value comps-suggestion__stat-value--accent">
            {condition}
          </span>
        </div>
        <div className="comps-suggestion__divider" />
        <div className="comps-suggestion__stat">
          <span className="comps-suggestion__stat-label">Confidence</span>
          <span className="comps-suggestion__stat-value">{percentage}%</span>
        </div>
        <button
          className="comps-suggestion__use-btn"
          onClick={() => onUseCondition(condition)}
          type="button"
        >
          Use this condition
        </button>
      </div>
    </div>
  );
}

// ── AddListingForm ────────────────────────────────────────────────────────────
export function AddListingForm({ onAdd, onClose, onDelete, initial }) {
  const isEditing = !!initial;

  const [form, setForm] = useState(
    initial ?? {
      platform:      "Depop",
      title:         "",
      category:      "Apparel",
      categoryOther: "",
      size:          "",
      condition:     "Good",
      price:         "",
      weightLbs:     "",
      notes:         "",
      imageUrl:      "",
    }
  );

  // Search term for comps — updated 400ms after the user stops typing in the title field
  const [compsQuery, setCompsQuery] = useState("");
  const debounceRef = useRef(null);

  const { suggestion, conditionSuggestion } = useComps(compsQuery);

  const handleChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));

    // Debounce comps lookup when the title changes
    if (key === "title") {
      clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => setCompsQuery(value), 400);
    }
  };

  const handleUsePrice = (price) =>
    setForm((prev) => ({ ...prev, price: price.toFixed(2) }));

  // Map the comp condition string to the closest value in the CONDITIONS list.
  // Falls back to the raw string if no match is found, so the dropdown stays valid.
  const handleUseCondition = (rawCondition) => {
    const match = CONDITIONS.find(
      (c) => c.toLowerCase() === rawCondition.toLowerCase()
    );
    setForm((prev) => ({ ...prev, condition: match ?? rawCondition }));
  };

  const handleSubmit = () => {
    if (!form.title.trim() || !form.price) return;
    const finalCategory =
      form.category === "Other" && form.categoryOther.trim()
        ? "Other: " + form.categoryOther.trim()
        : form.category;

    onAdd({
      ...form,
      category:  finalCategory,
      id:        isEditing ? form.id : Date.now(),
      price:     parseFloat(form.price),
      weightLbs: form.weightLbs ? parseFloat(form.weightLbs) : null,
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

        <div className="form-panel__header">
          <h3 className="form-panel__title">{isEditing ? "Edit Listing" : "New Listing"}</h3>
          <button className="form-panel__close" onClick={onClose}>X</button>
        </div>

        <ImageUpload value={form.imageUrl} onChange={handleChange} />

        <div className="form-grid">
          <Field label="Platform" fieldKey="platform" value={form.platform} onChange={handleChange} options={PLATFORMS.slice(1)} />
          <Field label="Category" fieldKey="category" value={form.category} onChange={handleChange} options={CATEGORIES} />

          {form.category === "Other" && (
            <div className="form-grid--full">
              <Field
                label="Describe Category"
                fieldKey="categoryOther"
                value={form.categoryOther}
                onChange={handleChange}
                placeholder="e.g. Musical Instruments, Sports Gear..."
              />
            </div>
          )}

          <div className="form-grid--full">
            <Field label="Title" fieldKey="title" value={form.title} onChange={handleChange} />
          </div>

          {/* Price comps suggestion appears directly below the title */}
          {suggestion && (
            <div className="form-grid--full">
              <CompsSuggestion suggestion={suggestion} onUsePrice={handleUsePrice} />
            </div>
          )}

          <Field label="Size"      fieldKey="size"      value={form.size}      onChange={handleChange} />
          <Field label="Condition" fieldKey="condition" value={form.condition} onChange={handleChange} options={CONDITIONS} />

          {/* Condition suggestion appears directly below the Condition dropdown */}
          {conditionSuggestion && (
            <div className="form-grid--full">
              <ConditionSuggestion
                conditionSuggestion={conditionSuggestion}
                onUseCondition={handleUseCondition}
              />
            </div>
          )}

          <Field label="Price ($)" fieldKey="price" value={form.price} onChange={handleChange} type="number" />

          <div className="form-field">
            <label>Item Weight (lbs)</label>
            <input
              type="number"
              min="0"
              step="0.1"
              value={form.weightLbs}
              placeholder="e.g. 1.5"
              onChange={(e) => handleChange("weightLbs", e.target.value)}
            />
          </div>

          <ShippingEstimate weightLbs={form.weightLbs} />

          <div className="form-field form-grid--full">
            <label>Notes</label>
            <textarea
              value={form.notes}
              onChange={(e) => handleChange("notes", e.target.value)}
            />
          </div>
        </div>

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