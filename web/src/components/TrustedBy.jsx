import React from 'react';

export default function TrustedBy() {
  const logos = [
    { name: 'airbnb', className: 'logo-airbnb' },
    { name: 'Shopify', className: 'logo-shopify' },
    { name: 'Notion', className: 'logo-notion' },
    { name: 'Linear', className: 'logo-linear' },
    { name: 'webflow', className: 'logo-webflow' },
    { name: 'Figma', className: 'logo-figma' },
    { name: 'slack', className: 'logo-slack' },
    { name: 'stripe', className: 'logo-stripe' },
    { name: '▲ Vercel', className: 'logo-vercel' },
    { name: 'Framer', className: 'logo-framer' },
  ];

  // 2x groups for seamless infinite loop
  const groups = [1, 2];

  return (
    <section className="trusted-section" aria-label="Trusted companies">
      <div className="trusted-label">
        Partnered with top-tier companies globally
      </div>

      <div className="trusted-marquee-container">
        <div className="trusted-marquee-track">
          {groups.map((gIndex) => (
            <div key={`trusted-group-${gIndex}`} className="trusted-logo-group">
              {logos.map((logo, index) => (
                <span
                  key={`logo-${gIndex}-${index}`}
                  className={`trusted-logo-text ${logo.className}`}
                >
                  {logo.name}
                </span>
              ))}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
