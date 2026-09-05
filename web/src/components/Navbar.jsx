import React from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';

export default function Navbar({ isDrawerOpen, setIsDrawerOpen }) {
  return (
    <header className="navbar-container">
      <nav className="navbar-inner">
        {/* Left: Logo */}
        <a href="#" className="navbar-logo">
          Alwayzz<span className="navbar-logo-tm">®</span>
        </a>

        {/* Right: Menu Pill Button */}
        <button
          className="menu-pill-btn"
          onClick={() => setIsDrawerOpen(!isDrawerOpen)}
          aria-label={isDrawerOpen ? "Close Menu" : "Open Menu"}
        >
          <span>Menu</span>
          {isDrawerOpen ? (
            <ChevronDown size={16} strokeWidth={2.2} />
          ) : (
            <ChevronUp size={16} strokeWidth={2.2} />
          )}
        </button>
      </nav>
    </header>
  );
}
