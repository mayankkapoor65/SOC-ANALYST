import { useEffect, useRef } from "react";
import { getRiskLevel, getRiskColor, formatTimestamp } from "../utils/riskHelpers";

export default function LiveSecurityFeed({ events }) {
  const feedRef = useRef(null);
  const prevCountRef = useRef(0);

  useEffect(() => {
    if ((events?.length || 0) > prevCountRef.current && feedRef.current) {
      feedRef.current.scrollTop = 0;
    }
    prevCountRef.current = events?.length || 0;
  }, [events]);

  if (!events?.length) {
    return <p className="empty-state">No live events in the current window.</p>;
  }

  return (
    <div className="live-feed" ref={feedRef}>
      {events.map((event, index) => {
        const level = getRiskLevel(event.risk_score);
        const isNew = index === 0;

        return (
          <div
            key={`${event.user_id}-${event.timestamp}-${index}`}
            className={`feed-item ${isNew ? "feed-item-new" : ""}`}
            style={{ borderLeftColor: getRiskColor(level) }}
          >
            <div className="feed-row">
              <span className="feed-user">{event.user_id}</span>
              <span
                className="severity-badge"
                style={{
                  color: getRiskColor(level),
                  borderColor: getRiskColor(level),
                }}
              >
                {level}
              </span>
            </div>
            <div className="feed-meta">
              <span>{event.event_type}</span>
              <span className="feed-score">Risk {event.risk_score}</span>
            </div>
            <div className="feed-time">{formatTimestamp(event.timestamp)}</div>
          </div>
        );
      })}
    </div>
  );
}
