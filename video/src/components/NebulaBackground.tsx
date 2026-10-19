import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { theme3d } from '../theme3d';

export const NebulaBackground: React.FC = () => {
  const frame = useCurrentFrame();

  const cloud1X = interpolate(Math.sin(frame * 0.015), [-1, 1], [35, 48]);
  const cloud1Y = interpolate(Math.cos(frame * 0.012), [-1, 1], [35, 48]);

  const cloud2X = interpolate(Math.cos(frame * 0.018), [-1, 1], [60, 75]);
  const cloud2Y = interpolate(Math.sin(frame * 0.014), [-1, 1], [45, 60]);

  // Subtle pulsing ambient light
  const ambientPulse = 0.85 + Math.sin(frame * 0.04) * 0.15;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme3d.colors.bg,
        overflow: 'hidden',
        pointerEvents: 'none',
      }}
    >
      {/* Subtle isometric background grid for 3D depth */}
      <div
        style={{
          position: 'absolute',
          inset: -200,
          backgroundImage: `
            radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.08) 0%, transparent 60%),
            linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px)
          `,
          backgroundSize: '100% 100%, 64px 64px, 64px 64px',
          opacity: 0.7,
        }}
      />

      {/* Deep Violet Nebula Cloud (matches reference Image 1 & 2) */}
      <div
        style={{
          position: 'absolute',
          left: `${cloud1X}%`,
          top: `${cloud1Y}%`,
          width: 950,
          height: 950,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(139, 92, 246, 0.32) 0%, rgba(99, 102, 241, 0.16) 45%, transparent 70%)',
          filter: 'blur(130px)',
          transform: `translate(-50%, -50%) scale(${ambientPulse})`,
        }}
      />

      {/* Indigo / Cyan Accent Glow */}
      <div
        style={{
          position: 'absolute',
          left: `${cloud2X}%`,
          top: `${cloud2Y}%`,
          width: 850,
          height: 850,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(79, 70, 229, 0.24) 0%, rgba(6, 182, 212, 0.12) 45%, transparent 70%)',
          filter: 'blur(140px)',
          transform: 'translate(-50%, -50%)',
        }}
      />

      {/* Center Specular Radial Core */}
      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: '50%',
          width: 600,
          height: 600,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(167, 139, 250, 0.14) 0%, transparent 60%)',
          filter: 'blur(90px)',
          transform: 'translate(-50%, -50%)',
        }}
      />

      {/* Soft Vignette Edge darkening */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(circle at center, transparent 35%, rgba(6, 5, 12, 0.85) 100%)',
        }}
      />
    </AbsoluteFill>
  );
};
