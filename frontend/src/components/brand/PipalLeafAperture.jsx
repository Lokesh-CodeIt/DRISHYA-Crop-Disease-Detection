/**
 * PipalLeafAperture.jsx - Architectural "Light Through a Leaf" Focal Backdrop
 *
 * Implements the DRISHYA core brand concept:
 * An organic Sacred Pipal leaf aperture through which warm lamp glow radiates
 * into deep espresso botanical darkness.
 */

import React from 'react';

export default function PipalLeafAperture({ className = '' }) {
  return (
    <div
      className={`pipal-aperture-wrapper ${className}`}
      style={{
        position: 'relative',
        width: '100%',
        maxWidth: '560px',
        height: '100%',
        minHeight: '440px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        pointerEvents: 'none',
      }}
      aria-hidden="true"
    >
      {/* Radiant Background Aura */}
      <div
        className="aperture-glow"
        style={{
          position: 'absolute',
          width: '380px',
          height: '380px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(242, 193, 78, 0.28) 0%, rgba(201, 154, 60, 0.12) 45%, rgba(28, 17, 10, 0) 70%)',
          filter: 'blur(32px)',
          transform: 'translate3d(0, 0, 0)',
        }}
      />

      {/* Architectural Pipal Leaf SVG Sculpture */}
      <svg
        className="aperture-leaf-svg"
        viewBox="0 0 500 650"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{
          width: '92%',
          maxWidth: '480px',
          height: 'auto',
          filter: 'drop-shadow(0 20px 40px rgba(12, 7, 3, 0.85))',
        }}
      >
        <defs>
          {/* Luminous Sunburst through Leaf */}
          <radialGradient id="apertureCoreGlow" cx="50%" cy="42%" r="55%">
            <stop offset="0%" stopColor="#FFF9E6" stopOpacity="0.85" />
            <stop offset="25%" stopColor="#F2C14E" stopOpacity="0.5" />
            <stop offset="55%" stopColor="#C99A3C" stopOpacity="0.2" />
            <stop offset="85%" stopColor="#3A2412" stopOpacity="0.05" />
            <stop offset="100%" stopColor="#1C110A" stopOpacity="0" />
          </radialGradient>

          {/* Leaf Translucency Gradient */}
          <linearGradient id="leafParchment" x1="50%" y1="0%" x2="50%" y2="100%">
            <stop offset="0%" stopColor="#F4EAD3" stopOpacity="0.08" />
            <stop offset="40%" stopColor="#C99A3C" stopOpacity="0.06" />
            <stop offset="100%" stopColor="#140C07" stopOpacity="0.35" />
          </linearGradient>

          {/* Vein Antique Gold Stroke */}
          <linearGradient id="veinGold" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#F4EAD3" stopOpacity="0.7" />
            <stop offset="50%" stopColor="#C99A3C" stopOpacity="0.45" />
            <stop offset="100%" stopColor="#8A5A2B" stopOpacity="0.2" />
          </linearGradient>
        </defs>

        {/* Ambient Backlight Disc */}
        <circle cx="250" cy="280" r="210" fill="url(#apertureCoreGlow)" />

        {/* Outer Architectural Ring */}
        <circle
          cx="250"
          cy="280"
          r="230"
          stroke="url(#veinGold)"
          strokeWidth="1"
          strokeOpacity="0.25"
          strokeDasharray="4 6"
        />

        {/* Sacred Pipal Leaf Form */}
        <path
          className="aperture-leaf-contour"
          d="M 250 560
             C 195 500, 70 380, 60 250
             C 50 140, 145 65, 230 52
             C 245 49, 250 20, 250 10
             C 250 20, 255 49, 270 52
             C 355 65, 450 140, 440 250
             C 430 380, 305 500, 250 560 Z"
          fill="url(#leafParchment)"
          stroke="url(#veinGold)"
          strokeWidth="2.5"
          strokeLinejoin="round"
        />

        {/* Central Rachis / Midrib Spinal Column */}
        <path
          className="aperture-midrib"
          d="M 250 550 Q 250 270, 250 15"
          stroke="url(#veinGold)"
          strokeWidth="2.8"
          strokeLinecap="round"
        />

        {/* Lateral Primary Veins - Left Network */}
        <path d="M 250 480 Q 180 435, 110 370" stroke="url(#veinGold)" strokeWidth="1.6" />
        <path d="M 250 415 Q 160 355, 95 275" stroke="url(#veinGold)" strokeWidth="1.6" />
        <path d="M 250 345 Q 155 275, 90 180" stroke="url(#veinGold)" strokeWidth="1.7" />
        <path d="M 250 270 Q 170 195, 120 115" stroke="url(#veinGold)" strokeWidth="1.6" />
        <path d="M 250 190 Q 195 130, 165 75" stroke="url(#veinGold)" strokeWidth="1.4" />
        <path d="M 250 115 Q 220 70, 205 45" stroke="url(#veinGold)" strokeWidth="1.2" />

        {/* Lateral Primary Veins - Right Network */}
        <path d="M 250 480 Q 320 435, 390 370" stroke="url(#veinGold)" strokeWidth="1.6" />
        <path d="M 250 415 Q 340 355, 405 275" stroke="url(#veinGold)" strokeWidth="1.6" />
        <path d="M 250 345 Q 345 275, 410 180" stroke="url(#veinGold)" strokeWidth="1.7" />
        <path d="M 250 270 Q 330 195, 380 115" stroke="url(#veinGold)" strokeWidth="1.6" />
        <path d="M 250 190 Q 305 130, 335 75" stroke="url(#veinGold)" strokeWidth="1.4" />
        <path d="M 250 115 Q 280 70, 295 45" stroke="url(#veinGold)" strokeWidth="1.2" />

        {/* Micro-reticulate Vein Webbing (Subtle botanical realism) */}
        <path d="M 180 435 Q 150 400, 140 430" stroke="url(#veinGold)" strokeWidth="0.8" strokeOpacity="0.5" />
        <path d="M 320 435 Q 350 400, 360 430" stroke="url(#veinGold)" strokeWidth="0.8" strokeOpacity="0.5" />
        <path d="M 160 355 Q 130 320, 125 350" stroke="url(#veinGold)" strokeWidth="0.8" strokeOpacity="0.5" />
        <path d="M 340 355 Q 370 320, 375 350" stroke="url(#veinGold)" strokeWidth="0.8" strokeOpacity="0.5" />
        <path d="M 155 275 Q 125 240, 115 270" stroke="url(#veinGold)" strokeWidth="0.8" strokeOpacity="0.5" />
        <path d="M 345 275 Q 375 240, 385 270" stroke="url(#veinGold)" strokeWidth="0.8" strokeOpacity="0.5" />

        {/* Central Luminous Point */}
        <circle cx="250" cy="260" r="6" fill="#FFF9E6" opacity="0.9" />
        <circle cx="250" cy="260" r="14" fill="#F2C14E" opacity="0.35" />
      </svg>
    </div>
  );
}
