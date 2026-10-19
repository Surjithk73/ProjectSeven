import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { continuousTheme } from '../theme';

interface CrosshairGridProps {
  progress?: number;
}

export const CrosshairGrid: React.FC<CrosshairGridProps> = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Crosshair lines entrance
  const lineEntrance = spring({
    frame,
    fps,
    config: { damping: 18, mass: 0.8, stiffness: 100 },
  });

  // Cycle symbols at center: v1.0 -> v1.4 -> v2.0
  const symbolIndex = Math.floor(interpolate(frame, [0, 25, 55, 85], [0, 1, 2, 2], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }));
  const symbols = ['v1.0', 'v1.4', 'v2.0'];
  const currentSymbol = symbols[symbolIndex];

  // Floating pill tags spring entrance
  const pill1Spring = spring({ frame: frame - 20, fps, config: { damping: 14, mass: 0.7, stiffness: 120 } });
  const pill2Spring = spring({ frame: frame - 35, fps, config: { damping: 14, mass: 0.7, stiffness: 120 } });
  const pill3Spring = spring({ frame: frame - 50, fps, config: { damping: 14, mass: 0.7, stiffness: 120 } });

  // Floating drift
  const driftY = Math.sin(frame * 0.05) * 5;

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        pointerEvents: 'none',
      }}
    >
      {/* Lower Third Volumetric Ambient Emerald/Teal Glow (matching ref_01.png) */}
      <div
        style={{
          position: 'absolute',
          bottom: -100,
          left: '50%',
          transform: 'translateX(-50%)',
          width: 700,
          height: 500,
          borderRadius: '50%',
          background: 'radial-gradient(ellipse at center, rgba(16, 185, 129, 0.28) 0%, rgba(14, 56, 43, 0.15) 50%, transparent 75%)',
          filter: 'blur(90px)',
        }}
      />

      {/* Hairline Crosshair Lines */}
      <svg
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
        }}
      >
        {/* Vertical Line */}
        <line
          x1="360"
          y1="0"
          x2="360"
          y2="1280"
          stroke="rgba(255, 255, 255, 0.08)"
          strokeWidth="1.2"
          strokeDasharray="1280"
          strokeDashoffset={(1 - lineEntrance) * 1280}
        />
        {/* Horizontal Line */}
        <line
          x1="0"
          y1="640"
          x2="720"
          y2="640"
          stroke="rgba(255, 255, 255, 0.08)"
          strokeWidth="1.2"
          strokeDasharray="720"
          strokeDashoffset={(1 - lineEntrance) * 720}
        />
      </svg>

      {/* Central Node Badge at Crosshair Intersection */}
      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: '50%',
          transform: `translate(-50%, -50%) translateY(${driftY}px) scale(${lineEntrance})`,
          width: 48,
          height: 34,
          borderRadius: 8,
          backgroundColor: '#1E1E24',
          border: '1px solid rgba(255, 255, 255, 0.18)',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: continuousTheme.fonts.mono,
          fontSize: 13,
          fontWeight: 700,
          color: currentSymbol === 'v2.0' ? continuousTheme.colors.amberGlow : '#FFFFFF',
          transition: 'all 0.2s ease',
          zIndex: 10,
        }}
      >
        {currentSymbol}
      </div>

      {/* Floating Pill Tag 1 (Top Left) */}
      <div
        style={{
          position: 'absolute',
          left: 200,
          top: 500,
          padding: '6px 14px',
          borderRadius: 20,
          backgroundColor: 'rgba(25, 25, 30, 0.75)',
          border: '1px solid rgba(255, 255, 255, 0.22)',
          fontFamily: continuousTheme.fonts.mono,
          fontSize: 11,
          color: '#E4E4E7',
          transform: `scale(${pill1Spring}) translateY(${driftY * 0.8}px)`,
          opacity: pill1Spring,
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}
      >
        <span>v1</span>
        <span style={{ color: 'rgba(255,255,255,0.4)' }}>|</span>
        <span style={{ color: continuousTheme.colors.ambientEmerald }}>Stable</span>
      </div>

      {/* Floating Pill Tag 2 (Top Right) */}
      <div
        style={{
          position: 'absolute',
          right: 170,
          top: 530,
          padding: '6px 14px',
          borderRadius: 20,
          backgroundColor: 'rgba(25, 25, 30, 0.75)',
          border: '1px solid rgba(255, 255, 255, 0.22)',
          fontFamily: continuousTheme.fonts.mono,
          fontSize: 11,
          color: '#E4E4E7',
          transform: `scale(${pill2Spring}) translateY(${driftY * 1.2}px)`,
          opacity: pill2Spring,
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}
      >
        <span>v2</span>
        <span style={{ color: 'rgba(255,255,255,0.4)' }}>|</span>
        <span style={{ color: continuousTheme.colors.amberGlow }}>Breaking</span>
      </div>

      {/* Floating Pill Tag 3 (Left Edge) */}
      <div
        style={{
          position: 'absolute',
          left: 170,
          top: 670,
          padding: '6px 12px',
          borderRadius: 20,
          backgroundColor: 'rgba(25, 25, 30, 0.75)',
          border: '1px solid rgba(255, 255, 255, 0.22)',
          fontFamily: continuousTheme.fonts.mono,
          fontSize: 11,
          color: '#A1A1AA',
          transform: `scale(${pill3Spring}) translateY(${driftY * 0.9}px)`,
          opacity: pill3Spring,
        }}
      >
        No Notice
      </div>
    </div>
  );
};
