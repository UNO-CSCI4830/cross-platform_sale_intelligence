import "./ListingCard.css";
import { Badge, ConditionDots } from "../Badge";
import { COLORS, PLATFORM_COLORS } from "../../constants/data";

// Displays a single listing as a card in the grid view.
// Props: listing (object)
export function GridCard({ listing }) {
  const pc = PLATFORM_COLORS[listing.platform] || COLORS.accent;
  const hasFlag = listing.stains || listing.damage || listing.fading;

  return (
    <div
      className="grid-card"
      style={{ borderTop: `3px solid ${pc}` }}
    >
      <div className="grid-card__header">
        <Badge label={listing.platform} color={pc} />
        {hasFlag && (
          <span className="grid-card__flag-label">⚠ FLAG</span>
        )}
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
        <div className="grid-card__flags">
          <FlagIcon active={listing.stains} />
          <span className="grid-card__flag-text">stain</span>
          <FlagIcon active={listing.damage} />
          <span className="grid-card__flag-text">dmg</span>
          <FlagIcon active={listing.fading} />
          <span className="grid-card__flag-text">fade</span>
        </div>
      </div>

      {listing.notes && (
        <p className="grid-card__notes">"{listing.notes}"</p>
      )}
    </div>
  );
}
