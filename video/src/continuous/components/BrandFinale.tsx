import React from 'react';
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { IridescentSphere } from './IridescentSphere';
import { ArrowRight } from 'lucide-react';

interface BrandFinaleProps {
  progress?: number;
}

export const BrandFinale: React.FC<BrandFinaleProps> = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const sphereEntrance = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 120 },
  });

  const textEntrance = spring({
    frame: frame - 15,
    fps,
    config: { damping: 15, mass: 0.8, stiffness: 110 },
  });

  const buttonEntrance = spring({
    frame: frame - 28,
    fps,
    config: { damping: 14, mass: 0.7, stiffness: 120 },
  });

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        pointerEvents: 'none',
      }}
    >
      {/* Central Hero Sphere (scaling down to logo badge) */}
      <div
        style={{
          transform: `scale(${sphereEntrance})`,
          opacity: sphereEntrance,
          marginBottom: 28,
        }}
      >
        <IridescentSphere size={105} />
      </div>

      {/* Bold Minimal Brand Title (matching ref2_10.png) */}
      <div
        style={{
          transform: `scale(${textEntrance})`,
          opacity: textEntrance,
          textAlign: 'center',
        }}
      >
        <h1
          style={{
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            fontSize: 54,
            fontWeight: 700,
            color: '#111111',
            letterSpacing: '-0.04em',
            margin: 0,
          }}
        >
          APIShield
        </h1>
        <p
          style={{
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            fontSize: 18,
            fontWeight: 400,
            color: '#71717A',
            letterSpacing: '-0.02em',
            marginTop: 10,
            maxWidth: 380,
            lineHeight: 1.35,
          }}
        >
          Autonomous API contract healing for resilient production software
        </p>
      </div>

      {/* Tactile Pill CTA Button (matching ref2_10.png) */}
      <div
        style={{
          marginTop: 34,
          transform: `scale(${buttonEntrance})`,
          opacity: buttonEntrance,
          padding: '14px 32px',
          borderRadius: 30,
          backgroundColor: '#FFFFFF',
          border: '1.5px solid rgba(0, 0, 0, 0.12)',
          boxShadow: '0 10px 25px rgba(0, 0, 0, 0.08), inset 0 1px 1px #FFFFFF',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
        }}
      >
        <span
          style={{
            fontFamily: 'Inter, -apple-system, sans-serif',
            fontSize: 16,
            fontWeight: 500,
            color: '#111111',
            letterSpacing: '-0.02em',
          }}
        >
          Try for free today
        </span>
        <ArrowRight size={16} color="#111111" />
      </div>
    </div>
  );
};
