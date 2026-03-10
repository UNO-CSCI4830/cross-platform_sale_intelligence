import "./ListingCard.css";
import { Badge, ConditionDots } from "../Badge";
import { COLORS, PLATFORM_COLORS } from "../../constants/data";

// Displays a single listing as a card in the grid view.
// Props:
//   listing  — listing object
//   onClick  — callback fired when the card is clicked (opens edit modal)
export function GridCard({ listing, onClick }) {
  const pc = PLATFORM_COLORS[listing.platform] || COLORS.accent;

  return (
    <div
      className="grid-card"
      style={{ borderTop: `3px solid ${pc}` }}
      onClick={onClick}
    >
      {/* Image area — only rendered when imageUrl is present */}
      {listing.imageUrl && (
        <div className="grid-card__image-wrap">
          <img
            src={listing.imageUrl}
            alt={listing.title}
            className="grid-card__image"
          />
        </div>
      )}

      <div className="grid-card__header">
        <Badge label={listing.platform} color={pc} />
      </div>

      <div>
        <p className="grid-card__title">{listing.title}</p>
        <p className="grid-card__meta">{listing.category} · Size {listing.size}</p>
      </div>

      <div className="grid-card__condition-row">
        <ConditionDots condition={listing.condition} />
        <span className="grid-card__condition-label">{listing.condition}</span>
      </div>

      <div className="grid-card__footer">
        <span className="grid-card__price">${listing.price}</span>
        {listing.weightLbs && (
          <span className="grid-card__weight">{listing.weightLbs} lb{listing.weightLbs !== 1 ? "s" : ""}</span>
        )}
      </div>

      {listing.notes && (
        <p className="grid-card__notes">"{listing.notes}"</p>
      )}
    </div>
  );
}
