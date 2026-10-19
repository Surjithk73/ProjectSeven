import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { continuousTheme } from '../theme';
import { RollingNumber } from './RollingNumber';
import { Zap, Globe, Box, BarChart2 } from 'lucide-react';

interface TactileSlabsProps {
  progress?: number;
}

export const TactileSlabs: React.FC<TactileSlabsProps> = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const entrance = spring({
    frame,
    fps,
    config: { damping: 16, mass: 0.9, stiffness: 100 },
  });

  // Layer elevation expansion:
  // Starts with 1 slab (frames 0-35), expands to 2 slabs (frame 35-70), expands to 3 slabs (frame 70+)
  const layer2Elev = spring({
    frame: frame - 25,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 110 },
  });
  const layer3Elev = spring({
    frame: frame - 55,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 110 },
  });

  const zGap = 42;
  const l2Z = interpolate(layer2Elev, [0, 1], [0, zGap]);
  const l3Z = interpolate(layer3Elev, [0, 1], [0, zGap * 2]);

  // Orbit rotation
  const orbitRotation = frame * 0.8;

  // Floating drift
  const floatY = Math.sin(frame * 0.05) * 6;

  // Orbiting badge springs
  const badge1 = spring({ frame: frame - 30, fps, config: { damping: 14, mass: 0.7, stiffness: 120 } });
  const badge2 = spring({ frame: frame - 45, fps, config: { damping: 14, mass: 0.7, stiffness: 120 } });
  const badge3 = spring({ frame: frame - 60, fps, config: { damping: 14, mass: 0.7, stiffness: 120 } });
  const badge4 = spring({ frame: frame - 75, fps, config: { damping: 14, mass: 0.7, stiffness: 120 } });

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        perspective: 1400,
        transformStyle: 'preserve-3d',
        pointerEvents: 'none',
      }}
    >
      {/* 2D Concentric Hairline Orbital Rings (matching ref_07.png & ref_11.png) */}
      <svg
        style={{
          position: 'absolute',
          width: 540,
          height: 540,
          left: '50%',
          top: '50%',
          transform: `translate(-50%, -50%) rotate(${orbitRotation * 0.4}deg)`,
          pointerEvents: 'none',
        }}
      >
        <circle cx="270" cy="270" r="160" fill="none" stroke="rgba(255, 255, 255, 0.16)" strokeWidth="1" />
        <circle cx="270" cy="270" r="220" fill="none" stroke="rgba(255, 255, 255, 0.12)" strokeWidth="1" strokeDasharray="4 6" />
        <circle cx="270" cy="270" r="260" fill="none" stroke="rgba(255, 255, 255, 0.08)" strokeWidth="1" />
      </svg>

      {/* 3D Isometric Stack Container */}
      <div
        style={{
          position: 'relative',
          width: 200,
          height: 200,
          transformStyle: 'preserve-3d',
          transform: `translateY(${floatY}px) scale(${entrance}) rotateX(55deg) rotateZ(-30deg)`,
        }}
      >
        {/* Slab 1 (Bottom) */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 24,
            background: 'linear-gradient(135deg, #1E293B 0%, #0F172A 60%, #D97706 100%)',
            boxShadow: `
              0 20px 40px rgba(0, 0, 0, 0.9),
              inset 0 1px 2px rgba(255, 255, 255, 0.4),
              inset -4px -4px 10px rgba(217, 119, 6, 0.5)
            `,
            border: '1.5px solid rgba(255, 255, 255, 0.25)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: 'translateZ(0px)',
          }}
        >
          <span style={{ fontFamily: continuousTheme.fonts.mono, fontSize: 24, fontWeight: 800, color: '#FFFFFF', opacity: 0.9 }}>
            &lt;/&gt;
          </span>
        </div>

        {/* Slab 2 (Middle) */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 24,
            background: 'linear-gradient(135deg, #1E293B 0%, #1E3A8A 50%, #D97706 100%)',
            boxShadow: `
              0 25px 45px rgba(0, 0, 0, 0.8),
              inset 0 1px 2px rgba(255, 255, 255, 0.5),
              inset -4px -4px 10px rgba(217, 119, 6, 0.6)
            `,
            border: '1.5px solid rgba(255, 255, 255, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: `translateZ(${l2Z}px)`,
            opacity: layer2Elev,
          }}
        >
          <span style={{ fontFamily: continuousTheme.fonts.mono, fontSize: 24, fontWeight: 800, color: '#FFFFFF', opacity: 0.9 }}>
            API
          </span>
        </div>

        {/* Slab 3 (Top) */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 24,
            background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 40%, #EA580C 100%)',
            boxShadow: `
              0 30px 60px rgba(0, 0, 0, 0.9),
              inset 0 1px 3px rgba(255, 255, 255, 0.7),
              inset -4px -4px 12px rgba(234, 88, 12, 0.7),
              0 0 35px rgba(37, 99, 235, 0.4)
            `,
            border: '1.5px solid rgba(255, 255, 255, 0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: `translateZ(${l3Z}px)`,
            opacity: layer3Elev,
          }}
        >
          <span style={{ fontFamily: continuousTheme.fonts.mono, fontSize: 24, fontWeight: 800, color: '#FFFFFF' }}>
            v2
          </span>
        </div>
      </div>

      {/* Floating HUD Card Top (matching ref_07.png & ref_11.png) */}
      <div
        style={{
          position: 'absolute',
          top: 400,
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: 'rgba(20, 20, 24, 0.88)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.16)',
          borderRadius: 14,
          padding: '10px 24px',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          zIndex: 20,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <RollingNumber
            items={['0', '48', '184', '422']}
            startFrame={10}
            durationPerItem={22}
            height={36}
            fontSize={28}
            fontWeight={700}
            color="#FFFFFF"
          />
          <span style={{ fontFamily: continuousTheme.fonts.mono, fontSize: 13, color: continuousTheme.colors.amberGlow, fontWeight: 700 }}>
            ERR
          </span>
        </div>

        <div style={{ width: 1, height: 20, backgroundColor: 'rgba(255,255,255,0.15)' }} />

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: '#A1A1AA' }}>
          <Zap size={18} color="#FFFFFF" />
          <Globe size={18} color="#FFFFFF" />
        </div>
      </div>

      {/* Floating HUD Card Bottom (matching ref_07.png & ref_11.png) */}
      <div
        style={{
          position: 'absolute',
          bottom: 390,
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: 'rgba(20, 20, 24, 0.88)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.16)',
          borderRadius: 14,
          padding: '10px 24px',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          zIndex: 20,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: '#A1A1AA' }}>
          <Box size={18} color="#FFFFFF" />
          <BarChart2 size={18} color="#FFFFFF" />
        </div>

        <div style={{ width: 1, height: 20, backgroundColor: 'rgba(255,255,255,0.15)' }} />

        <div style={{ fontFamily: continuousTheme.fonts.sans, fontSize: 18, fontWeight: 700, color: '#FFFFFF' }}>
          /MIN
        </div>
      </div>

      {/* Orbiting Callout Badge 1 (Left - schema drift) */}
      <div
        style={{
          position: 'absolute',
          left: 100,
          top: 610,
          padding: '6px 14px',
          borderRadius: 20,
          border: '1px solid rgba(255, 255, 255, 0.25)',
          backgroundColor: 'rgba(18, 18, 22, 0.8)',
          backdropFilter: 'blur(10px)',
          fontFamily: continuousTheme.fonts.sans,
          fontSize: 12,
          fontWeight: 500,
          color: '#E4E4E7',
          transform: `scale(${badge1})`,
          opacity: badge1,
        }}
      >
        schema drift
      </div>

      {/* Orbiting Callout Badge 2 (Right - silent 422s) */}
      <div
        style={{
          position: 'absolute',
          right: 90,
          top: 550,
          padding: '6px 14px',
          borderRadius: 20,
          border: '1px solid rgba(255, 255, 255, 0.25)',
          backgroundColor: 'rgba(18, 18, 22, 0.8)',
          backdropFilter: 'blur(10px)',
          fontFamily: continuousTheme.fonts.sans,
          fontSize: 12,
          fontWeight: 500,
          color: '#E4E4E7',
          transform: `scale(${badge2})`,
          opacity: badge2,
        }}
      >
        silent 422s
      </div>

      {/* Orbiting Callout Badge 3 (Top Left - broken checkouts) */}
      <div
        style={{
          position: 'absolute',
          left: 140,
          top: 490,
          padding: '6px 14px',
          borderRadius: 20,
          border: '1px solid rgba(255, 255, 255, 0.25)',
          backgroundColor: 'rgba(18, 18, 22, 0.8)',
          backdropFilter: 'blur(10px)',
          fontFamily: continuousTheme.fonts.sans,
          fontSize: 12,
          fontWeight: 500,
          color: continuousTheme.colors.amberGlow,
          transform: `scale(${badge3})`,
          opacity: badge3,
        }}
      >
        broken checkouts
      </div>

      {/* Orbiting Callout Badge 4 (Bottom Right - manual fire drills) */}
      <div
        style={{
          position: 'absolute',
          right: 120,
          bottom: 470,
          padding: '6px 14px',
          borderRadius: 20,
          border: '1px solid rgba(255, 255, 255, 0.25)',
          backgroundColor: 'rgba(18, 18, 22, 0.8)',
          backdropFilter: 'blur(10px)',
          fontFamily: continuousTheme.fonts.sans,
          fontSize: 12,
          fontWeight: 500,
          color: '#E4E4E7',
          transform: `scale(${badge4})`,
          opacity: badge4,
        }}
      >
        emergency hotfix
      </div>
    </div>
  );
};
