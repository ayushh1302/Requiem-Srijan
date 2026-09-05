import React, { useState } from 'react';
import Navbar from './components/Navbar';
import MenuDrawer from './components/MenuDrawer';
import Hero from './components/Hero';
import TrustedBy from './components/TrustedBy';

export default function App() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  return (
    <div className="alwayzz-app">
      {/* Fixed Navbar */}
      <Navbar
        isDrawerOpen={isDrawerOpen}
        setIsDrawerOpen={setIsDrawerOpen}
      />

      {/* Full-Screen Drawer Menu */}
      <MenuDrawer
        isOpen={isDrawerOpen}
        setIsOpen={setIsDrawerOpen}
      />

      {/* Hero Section */}
      <main>
        <Hero />
        <TrustedBy />
      </main>
    </div>
  );
}
