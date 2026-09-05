import React from 'react';
import CurvedLines from './CurvedLines';
import TickerMarquee from './TickerMarquee';

export default function Hero() {
  return (
    <section className="hero-section">
      {/* Decorative Pulsing Curved Lines */}
      <CurvedLines />

      {/* Hero Content */}
      <div className="hero-content">
        {/* Ticker Row */}
        <TickerMarquee />

        {/* Title */}
        <h1 className="hero-title">
          Premium creative{' '}
          <span className="hero-title-italic serif italic">alwayzz</span>
          <sup className="hero-title-sup">®</sup>{' '}
          on demand.
        </h1>

        {/* Subtitle */}
        <p className="hero-subtitle">
          A flexible design partnership for founders, brands, and agencies who
          want top craft delivered on their timeline.
        </p>

        {/* CTA Row */}
        <div className="cta-row">
          {/* Primary Button */}
          <a href="#plans" className="btn-primary">
            View Plans
          </a>

          {/* Book Button */}
          <a href="#book" className="btn-book">
            <img
              src="https://framerusercontent.com/images/hfneFL6CHBi5BnNvCeOaqU9HqE4.png"
              alt="Design Partner Avatar"
              className="book-avatar"
            />
            <div className="book-text-stack">
              <span className="book-text-primary">Chat for 15 minutes</span>
              <span className="book-text-secondary">
                Pick a slot <span className="green-status-dot" />
              </span>
            </div>
          </a>
        </div>
      </div>

      {/* Progressive Blur at Bottom */}
      <div className="progressive-blur" aria-hidden="true" />
    </section>
  );
}
