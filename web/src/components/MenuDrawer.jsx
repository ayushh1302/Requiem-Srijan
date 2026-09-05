import React from 'react';

export default function MenuDrawer({ isOpen, setIsOpen }) {
  const links = [
    { label: 'Projects', href: '#projects' },
    { label: 'Plans', href: '#plans' },
    { label: 'Team', href: '#team' },
    { label: 'FAQs', href: '#faqs' },
    { label: 'Get in Touch', href: '#contact' },
  ];

  return (
    <div className={`menu-drawer-overlay ${isOpen ? 'open' : ''}`}>
      <div className="drawer-nav-links">
        {links.map((link) => (
          <a
            key={link.label}
            href={link.href}
            className="drawer-nav-item"
            onClick={() => setIsOpen(false)}
          >
            {link.label}
          </a>
        ))}
      </div>

      <div className="drawer-footer">
        © {new Date().getFullYear()} Alwayzz Creative Agency. All rights reserved.
      </div>
    </div>
  );
}
