import { useEffect, useState } from "react";

export default function AnimatedCounter({ value, duration = 800, decimals = 0 }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const target = Number(value) || 0;
    const start = display;
    const startTime = performance.now();

    const tick = (now) => {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = start + (target - start) * eased;
      setDisplay(current);
      if (progress < 1) requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);
  }, [value, duration]);

  return (
    <span className="animated-counter">
      {decimals > 0 ? display.toFixed(decimals) : Math.round(display).toLocaleString()}
    </span>
  );
}
