import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { theme3d } from '../theme3d';
import { GlowingOrbBadge } from '../components/GlowingOrbBadge';
import { FloatingMetricCard } from '../components/FloatingMetricCard';
import { GitPullRequest, CheckCircle2, ShieldCheck, Sparkles, Check } from 'lucide-react';

export const Scene5VerifiedPRFinale: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Phase 1: PR card appears (frames 0 - 65)
  // Phase 2: Hero finale transition (frames 65 - 140)
  const isFinale = frame >= 65;

  const prSpring = spring({
    frame,
    fps,
    config: { damping: 15, mass: 0.9, stiffness: 120 },
  });

  const finaleSpring = spring({
    frame: frame - 65,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 100 },
  });

  const camRotateX = interpolate(frame, [0, 140], [14, 6]);
  const camRotateY = interpolate(frame, [0, 140], [-6, 0]);
  const camZoom = interpolate(frame, [0, 140], [0.97, 1.05]);

  return (
    <AbsoluteFill
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        perspective: 1200,
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
        {/* Phase 1: GitHub Draft PR Card */}
        <div
          style={{
            position: 'absolute',
            width: 660,
            padding: 34,
            borderRadius: 28,
            backgroundColor: theme3d.colors.bgCard,
            backdropFilter: 'blur(24px)',
            border: '1.5px solid rgba(16, 185, 129, 0.4)',
            boxShadow: `0 30px 70px rgba(0, 0, 0, 0.8), 0 0 45px rgba(16, 185, 129, 0.25)`,
            transform: `scale(${isFinale ? 1 - finaleSpring * 0.4 : prSpring}) translateY(${isFinale ? -finaleSpring * 120 : 0}px)`,
            opacity: isFinale ? 1 - finaleSpring : 1,
            pointerEvents: 'none',
            zIndex: 10,
          }}
        >
          {/* Top highlight */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 1,
              background: 'linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.8), transparent)',
            }}
          />

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 42,
                  height: 42,
                  borderRadius: 14,
                  backgroundColor: 'rgba(16, 185, 129, 0.2)',
                  border: '1px solid rgba(16, 185, 129, 0.5)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: theme3d.colors.emerald,
                }}
              >
                <GitPullRequest size={22} />
              </div>
              <div>
                <div style={{ fontFamily: theme3d.fonts.sans, fontSize: 18, fontWeight: 700, color: '#FFFFFF' }}>
                  Pull Request #142 Ready
                </div>
                <div style={{ fontFamily: theme3d.fonts.mono, fontSize: 12, color: theme3d.colors.textSecondary }}>
                  apishield/fix-nexuspay-v2-drift ➔ main
                </div>
              </div>
            </div>

            <div
              style={{
                fontFamily: theme3d.fonts.mono,
                fontSize: 12,
                fontWeight: 700,
                color: theme3d.colors.emerald,
                backgroundColor: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.35)',
                padding: '6px 14px',
                borderRadius: 20,
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <Check size={14} />
              Mergeable
            </div>
          </div>

          <div
            style={{
              marginTop: 22,
              padding: '16px 20px',
              backgroundColor: 'rgba(0, 0, 0, 0.45)',
              borderRadius: 16,
              border: '1px solid rgba(255, 255, 255, 0.08)',
            }}
          >
            <div
              style={{
                fontFamily: theme3d.fonts.sans,
                fontSize: 14,
                fontWeight: 600,
                color: '#FFFFFF',
                marginBottom: 8,
              }}
            >
              fix(billing): adapt to NexusPay v2.0 schema requirements
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 16,
                fontFamily: theme3d.fonts.mono,
                fontSize: 12,
                color: theme3d.colors.textSecondary,
              }}
            >
              <span style={{ color: theme3d.colors.emerald }}>✔ 4/4 Pytest Passed</span>
              <span style={{ color: theme3d.colors.cyan }}>✔ 100% Invariants Preserved</span>
              <span>✔ 0 Human Edits</span>
            </div>
          </div>
        </div>

        {/* Phase 2: Radiant APIShield Hero Emblem */}
        {isFinale && (
          <div
            style={{
              position: 'absolute',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              transform: `scale(${finaleSpring})`,
              opacity: finaleSpring,
              zIndex: 20,
            }}
          >
            <GlowingOrbBadge size={220} icon="shield" />

            <div
              style={{
                marginTop: 28,
                textAlign: 'center',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
              }}
            >
              <h1
                style={{
                  fontFamily: theme3d.fonts.sans,
                  fontSize: 56,
                  fontWeight: 900,
                  letterSpacing: '-0.04em',
                  margin: 0,
                  background: 'linear-gradient(135deg, #FFFFFF 0%, #E0E7FF 40%, #A78BFA 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  filter: 'drop-shadow(0 4px 20px rgba(139, 92, 246, 0.5))',
                }}
              >
                APIShield
              </h1>
              <p
                style={{
                  fontFamily: theme3d.fonts.sans,
                  fontSize: 20,
                  fontWeight: 500,
                  color: theme3d.colors.textSecondary,
                  marginTop: 10,
                  maxWidth: 600,
                  lineHeight: 1.4,
                  letterSpacing: '-0.01em',
                }}
              >
                Autonomous API Contract Healing for Resilient Software
              </p>
              <div
                style={{
                  marginTop: 22,
                  fontFamily: theme3d.fonts.mono,
                  fontSize: 14,
                  fontWeight: 600,
                  color: theme3d.colors.cyan,
                  backgroundColor: 'rgba(6, 182, 212, 0.12)',
                  border: '1px solid rgba(6, 182, 212, 0.35)',
                  padding: '8px 24px',
                  borderRadius: 24,
                  letterSpacing: '0.05em',
                }}
              >
                Zero Downtime • Zero Silent Outages
              </div>
            </div>
          </div>
        )}

        {/* Floating Green / Emerald Success Metrics */}
        <FloatingMetricCard
          delay={10}
          label="Human Downtime"
          value="0 Minutes"
          trend="Autonomous"
          trendColor={theme3d.colors.emerald}
          icon={<ShieldCheck size={18} color={theme3d.colors.emerald} />}
          style={{
            position: 'absolute',
            left: 200,
            bottom: 240,
            transform: 'translateZ(50px) rotateY(15deg)',
          }}
        />

        <FloatingMetricCard
          delay={20}
          label="PR Status"
          value="Ready to Merge"
          trend="CI Passed"
          trendColor={theme3d.colors.emerald}
          icon={<CheckCircle2 size={18} color={theme3d.colors.emerald} />}
          style={{
            position: 'absolute',
            right: 200,
            top: 190,
            transform: 'translateZ(50px) rotateY(-15deg)',
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
          border: '1px solid rgba(16, 185, 129, 0.4)',
          padding: '12px 28px',
          borderRadius: 30,
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5), 0 0 25px rgba(16, 185, 129, 0.25)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}
      >
        <Sparkles size={18} color={theme3d.colors.emerald} />
        <span style={{ fontFamily: theme3d.fonts.sans, fontSize: 15, fontWeight: 600, color: '#FFFFFF' }}>
          Production healed automatically with verified pull requests before users ever notice
        </span>
      </div>
    </AbsoluteFill>
  );
};
