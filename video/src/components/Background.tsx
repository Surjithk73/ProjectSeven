import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { theme } from '../theme';

export const Background: React.FC = () => {
  const frame = useCurrentFrame();

  // Floating ambient glowing orbs
  const orb1X = interpolate(Math.sin(frame * 0.02), [-1, 1], [15, 35]);
  const orb1Y = interpolate(Math.cos(frame * 0.015), [-1, 1], [15, 35]);

  const orb2X = interpolate(Math.cos(frame * 0.018), [-1, 1], [65, 85]);
  const orb2Y = interpolate(Math.sin(frame * 0.022), [-1, 1], [55, 75]);

  const orb3X = interpolate(Math.sin(frame * 0.01), [-1, 1], [40, 60]);
  const orb3Y = interpolate(Math.cos(frame * 0.012), [-1, 1], [70, 90]);

  // Subtle grid pulse
  const gridOpacity = interpolate(Math.sin(frame * 0.03), [-1, 1], [0.03, 0.07]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.colors.bgDark,
        overflow: 'hidden',
        pointerEvents: 'none',
      }}
    >
      {/* Dynamic blurred glow orbs */}
      <div
        style={{
          position: 'absolute',
          left: `${orb1X}%`,
          top: `${orb1Y}%`,
          width: 700,
          height: 700,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(6, 182, 212, 0.18) 0%, transparent 70%)',
          filter: 'blur(90px)',
          transform: 'translate(-50%, -50%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: `${orb2X}%`,
          top: `${orb2Y}%`,
          width: 800,
          height: 800,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(139, 92, 246, 0.16) 0%, transparent 70%)',
          filter: 'blur(100px)',
          transform: 'translate(-50%, -50%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: `${orb3X}%`,
          top: `${orb3Y}%`,
          width: 650,
          height: 650,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(59, 130, 246, 0.14) 0%, transparent 70%)',
          filter: 'blur(80px)',
          transform: 'translate(-50%, -50%)',
        }}
      />

      {/* Modern subtle engineering grid overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `
            linear-gradient(to right, rgba(255, 255, 255, ${gridOpacity}) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, ${gridOpacity}) 1px, transparent 1px)
          `,
          backgroundSize: '80px 80px',
        }}
      />

      {/* Vignette edge shading */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(circle at center, transparent 40%, rgba(5, 8, 16, 0.85) 100%)',
        }}
      />
    </AbsoluteFill>
  );
};
