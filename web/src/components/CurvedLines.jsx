import React from 'react';

export default function CurvedLines() {
  const lineCount = 20;
  const lines = Array.from({ length: lineCount }, (_, i) => ({
    id: i,
    delay: `${i * 0.25}s`,
    width: `${60 + i * 10}px`,
  }));

  const mobileLines = Array.from({ length: 12 }, (_, i) => ({
    id: i,
    delay: `${i * 0.25}s`,
    width: `${120 + i * 20}px`,
  }));

  return (
    <div className="curved-lines-container" aria-hidden="true">
      {/* Desktop Left Side (20 lines) */}
      <div className="curved-lines-side curved-lines-left">
        {lines.map((line) => (
          <div
            key={`left-${line.id}`}
            className="curved-line left"
            style={{
              width: line.width,
              animationDelay: line.delay,
            }}
          />
        ))}
      </div>

      {/* Desktop Right Side (20 lines) */}
      <div className="curved-lines-side curved-lines-right">
        {lines.map((line) => (
          <div
            key={`right-${line.id}`}
            className="curved-line right"
            style={{
              width: line.width,
              animationDelay: line.delay,
            }}
          />
        ))}
      </div>

      {/* Mobile Top Horizontal Lines */}
      <div className="curved-lines-mobile">
        {mobileLines.map((line) => (
          <div
            key={`mobile-${line.id}`}
            className="curved-line-mobile-item"
            style={{
              width: line.width,
              animationDelay: line.delay,
            }}
          />
        ))}
      </div>
    </div>
  );
}
