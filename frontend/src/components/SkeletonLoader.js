export default function SkeletonLoader() {
  return (
    <div className="sentinel-app skeleton-screen">
      <div className="skeleton-sidebar" />
      <div className="skeleton-main">
        <div className="skeleton-bar" />
        <div className="skeleton-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
        <div className="skeleton-chart" />
        <div className="skeleton-chart" />
      </div>
    </div>
  );
}
