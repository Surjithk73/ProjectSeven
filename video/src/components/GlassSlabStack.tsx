import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { theme3d } from '../theme3d';
import { GitPullRequest, Code2, Cpu } from 'lucide-react';

interface GlassSlabStackProps {
  progress?: number;
}

export const GlassSlabStack: React.FC<GlassSlabStackProps> = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const stackSpring = spring({
    frame,
    fps,
    config: { damping: 16, mass: 1, stiffness: 100 },
  });

  // Dynamic subtle tilt breathing
  const tiltX = 52 + Math.sin(frame * 0.04) * 2;
  const tiltZ = -30 + Math.cos(frame * 0.03) * 1.5;

  // Staggered layer expansion along Z axis
  const zOffset = interpolate(stackSpring, [0, 1], [0, 85]);

  return (
    <div
      style={{
        position: 'relative',
        width: 640,
        height: 480,
        perspective: 1400,
        transformStyle: 'preserve-3d',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          width: 520,
          height: 280,
          position: 'relative',
          transformStyle: 'preserve-3d',
          transform: `scale(${stackSpring}) rotateX(${tiltX}deg) rotateZ(${tiltZ}deg)`,
        }}
      >
        {/* Layer 3 (Bottom): Semantic Intent Graph Engine */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 24,
            backgroundColor: 'rgba(15, 12, 35, 0.85)',
            border: `1.5px solid ${theme3d.colors.cyan}66`,
            boxShadow: `0 35px 70px rgba(0, 0, 0, 0.8), 0 0 40px ${theme3d.colors.cyan}33`,
            transform: `translateZ(${-zOffset}px)`,
            padding: 24,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            backdropFilter: 'blur(20px)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  backgroundColor: `${theme3d.colors.cyan}22`,
                  border: `1px solid ${theme3d.colors.cyan}55`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Cpu size={18} color={theme3d.colors.cyan} />
              </div>
              <span
                style={{
                  fontFamily: theme3d.fonts.sans,
                  fontSize: 16,
                  fontWeight: 700,
                  color: '#FFFFFF',
                }}
              >
                Layer 03 • Semantic Intent Graph
              </span>
            </div>
            <span
              style={{
                fontFamily: theme3d.fonts.mono,
                fontSize: 12,
                color: theme3d.colors.cyan,
                backgroundColor: `${theme3d.colors.cyan}1A`,
                padding: '4px 10px',
                borderRadius: 6,
                fontWeight: 600,
              }}
            >
              100% Invariants Preserved
            </span>
          </div>

          <div
            style={{
              fontFamily: theme3d.fonts.mono,
              fontSize: 13,
              color: theme3d.colors.textSecondary,
              backgroundColor: 'rgba(0,0,0,0.4)',
              padding: '12px 16px',
              borderRadius: 12,
              border: '1px solid rgba(255,255,255,0.06)',
              display: 'flex',
              flexDirection: 'column',
              gap: 4,
            }}
          >
            <div style={{ color: theme3d.colors.emerald }}>✔ Pre-condition: amount &gt; 0 in cents</div>
            <div style={{ color: theme3d.colors.cyan }}>✔ Idempotency-Key preserved in header</div>
          </div>
        </div>

        {/* Layer 2 (Middle): Client AST Call Site */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 24,
            backgroundColor: 'rgba(25, 20, 48, 0.85)',
            border: `1.5px solid ${theme3d.colors.violet}66`,
            boxShadow: `0 25px 60px rgba(0, 0, 0, 0.7), 0 0 35px ${theme3d.colors.violet}33`,
            transform: `translateZ(0px)`,
            padding: 24,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            backdropFilter: 'blur(20px)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  backgroundColor: `${theme3d.colors.violet}22`,
                  border: `1px solid ${theme3d.colors.violet}55`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Code2 size={18} color={theme3d.colors.violet} />
              </div>
              <span
                style={{
                  fontFamily: theme3d.fonts.sans,
                  fontSize: 16,
                  fontWeight: 700,
                  color: '#FFFFFF',
                }}
              >
                Layer 02 • Client AST Call Site
              </span>
            </div>
            <span
              style={{
                fontFamily: theme3d.fonts.mono,
                fontSize: 12,
                color: theme3d.colors.violet,
                backgroundColor: `${theme3d.colors.violet}1A`,
                padding: '4px 10px',
                borderRadius: 6,
                fontWeight: 600,
              }}
            >
              src/services/billing.py:48
            </span>
          </div>

          <div
            style={{
              fontFamily: theme3d.fonts.mono,
              fontSize: 13,
              backgroundColor: 'rgba(0,0,0,0.5)',
              padding: '12px 16px',
              borderRadius: 12,
              border: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <span style={{ color: theme3d.colors.rose }}>- response = client.charge(amount, cur)</span>
            <br />
            <span style={{ color: theme3d.colors.emerald }}>+ response = client.charge_v2(amount_in_cents, currency)</span>
          </div>
        </div>

        {/* Layer 1 (Top): OpenAPI 3.1 Contract Diff */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 24,
            backgroundColor: 'rgba(35, 28, 68, 0.88)',
            border: `1.5px solid rgba(255, 255, 255, 0.25)`,
            boxShadow: `
              0 30px 60px rgba(0, 0, 0, 0.8),
              inset 0 1px 2px rgba(255, 255, 255, 0.5),
              0 0 40px rgba(139, 92, 246, 0.4)
            `,
            transform: `translateZ(${zOffset}px)`,
            padding: 24,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            backdropFilter: 'blur(20px)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <GitPullRequest size={18} color="#FFFFFF" />
              </div>
              <span
                style={{
                  fontFamily: theme3d.fonts.sans,
                  fontSize: 16,
                  fontWeight: 700,
                  color: '#FFFFFF',
                }}
              >
                Layer 01 • Schema Contract Drift
              </span>
            </div>
            <span
              style={{
                fontFamily: theme3d.fonts.mono,
                fontSize: 12,
                color: theme3d.colors.rose,
                backgroundColor: `${theme3d.colors.rose}1A`,
                border: `1px solid ${theme3d.colors.rose}44`,
                padding: '4px 10px',
                borderRadius: 6,
                fontWeight: 600,
              }}
            >
              Breaking Drift Detected
            </span>
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontFamily: theme3d.fonts.mono,
              fontSize: 12,
              backgroundColor: 'rgba(0,0,0,0.5)',
              padding: '12px 16px',
              borderRadius: 12,
              border: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <div>
              <span style={{ color: theme3d.colors.textMuted }}>DIFF: </span>
              <span style={{ color: theme3d.colors.rose }}>POST /v2/payments</span>
            </div>
            <div style={{ color: theme3d.colors.emerald }}>Auto-mapped to AST</div>
          </div>
        </div>

        {/* Floating Callout Node (Matching user Image 3) */}
        <div
          style={{
            position: 'absolute',
            right: -100,
            top: 20,
            transform: `translateZ(${zOffset * 1.2}px)`,
            display: 'flex',
            alignItems: 'center',
            gap: 12,
          }}
        >
          {/* Connector Line */}
          <div
            style={{
              width: 60,
              height: 2,
              background: 'linear-gradient(90deg, rgba(139, 92, 246, 0.8), transparent)',
            }}
          />
          {/* Circular Node */}
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: '50%',
              backgroundColor: theme3d.colors.violet,
              boxShadow: '0 0 15px #8B5CF6, 0 0 30px #8B5CF6',
              border: '2px solid #FFFFFF',
            }}
          />
        </div>
      </div>
    </div>
  );
};
