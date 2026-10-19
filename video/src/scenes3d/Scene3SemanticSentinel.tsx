import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { theme3d } from '../theme3d';
import { GlowingOrbBadge } from '../components/GlowingOrbBadge';
import { GlassSlabStack } from '../components/GlassSlabStack';
import { FloatingMetricCard } from '../components/FloatingMetricCard';
import { ShieldCheck, Network, Binary } from 'lucide-react';

export const Scene3SemanticSentinel: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Phase 1: Glowing Orb rises (frames 0 - 50)
  // Phase 2: Isometric slabs expand on right (frames 40 - 150)
  const morphProgress = spring({
    frame: frame - 35,
    fps,
    config: { damping: 16, mass: 1, stiffness: 90 },
  });

  const camRotateY = interpolate(frame, [0, 150], [-8, 12]);
  const camRotateX = interpolate(frame, [0, 150], [14, 18]);
  const camZoom = interpolate(frame, [0, 150], [0.96, 1.04]);

  return (
    <AbsoluteFill
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        perspective: 1400,
        transformStyle: 'preserve-3d',
      }}
    >
      {/* 3D Scene Container */}
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transform: `scale(${camZoom}) rotateX(${camRotateX}deg) rotateY(${camRotateY}deg)`,
          transformStyle: 'preserve-3d',
          position: 'relative',
        }}
      >
        {/* Left / Center: Glowing Orb Badge (Image 1 style) */}
        <div
          style={{
            position: 'absolute',
            left: interpolate(morphProgress, [0, 1], [960, 480]),
            top: '46%',
            transform: 'translate(-50%, -50%)',
            zIndex: 10,
          }}
        >
          <GlowingOrbBadge
            size={190}
            icon="shield"
            label="APIShield Sentinel"
            sublabel="Nightly Autonomous Watcher"
          />
        </div>

        {/* Right: Isometric Glass Slab Stack (Image 3 style) */}
        {frame > 30 && (
          <div
            style={{
              position: 'absolute',
              right: 220,
              top: '42%',
              transform: `translateY(-50%) translateX(${interpolate(morphProgress, [0, 1], [100, 0])}px)`,
              opacity: interpolate(morphProgress, [0, 1], [0, 1]),
              zIndex: 5,
            }}
          >
            <GlassSlabStack />
          </div>
        )}

        {/* Floating Metrics */}
        <FloatingMetricCard
          delay={15}
          label="Contract Drift"
          value="Detected"
          trend="Nightly Scan"
          trendColor={theme3d.colors.cyan}
          icon={<Network size={18} color={theme3d.colors.cyan} />}
          style={{
            position: 'absolute',
            left: 200,
            bottom: 220,
            transform: 'translateZ(40px)',
          }}
        />

        <FloatingMetricCard
          delay={25}
          label="AST Call Sites"
          value="1 Site Found"
          trend="Exact Line"
          trendColor={theme3d.colors.violet}
          icon={<Binary size={18} color={theme3d.colors.violet} />}
          style={{
            position: 'absolute',
            right: 200,
            top: 170,
            transform: 'translateZ(50px)',
          }}
        />
      </div>

      {/* Subtitle Pill */}
      <div
        style={{
          position: 'absolute',
          bottom: 48,
          backgroundColor: 'rgba(15, 12, 35, 0.85)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(139, 92, 246, 0.4)',
          padding: '12px 28px',
          borderRadius: 30,
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5), 0 0 25px rgba(139, 92, 246, 0.3)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}
      >
        <ShieldCheck size={18} color={theme3d.colors.violet} />
        <span style={{ fontFamily: theme3d.fonts.sans, fontSize: 15, fontWeight: 600, color: '#FFFFFF' }}>
          Nightly Sentinel monitors contract changes & builds the Semantic Intent Graph
        </span>
      </div>
    </AbsoluteFill>
  );
};
