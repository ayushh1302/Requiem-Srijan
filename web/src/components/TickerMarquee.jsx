import React from 'react';

export default function TickerMarquee() {
  const items = [
    'Brand Identity',
    'App Development',
    'Visual Design',
    'Creative Video',
    'Iconography',
  ];

  // 4x duplicated rows for seamless loop
  const groups = [1, 2, 3, 4];

  return (
    <div className="ticker-container" aria-label="Services offered">
      <div className="ticker-track">
        {groups.map((gIndex) => (
          <div key={`group-${gIndex}`} className="ticker-group">
            {items.map((item, index) => (
              <span key={`item-${gIndex}-${index}`} className="ticker-pill">
                {item}
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
