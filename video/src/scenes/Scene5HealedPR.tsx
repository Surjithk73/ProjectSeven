import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { ShieldCheck, GitPullRequest, ArrowRight, CheckCircle2 } from 'lucide-react';
import { theme } from '../theme';

export const Scene5HealedPR: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring for PR card
  const prCardEntrance = spring({
    frame: frame - 5,
    fps,
    config: { damping: 14, mass: 0.6 },
  });

  // Logo outro reveal (starting frame 55)
  const logoReveal = spring({
    frame: frame - 55,
    fps,
    config: { damping: 12, mass: 0.5 },
  });

  // Electric surge glow
  const glowBurst = interpolate(Math.sin(frame * 0.15), [-1, 1], [0.4, 0.9]);

  return (
    <AbsoluteFill
      style={{
        padding: '110px 80px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
      }}
    >
      {/* 1. GITHUB DRAFT PULL REQUEST CARD (Appears First) */}
      {frame < 60 && (
        <div
          style={{
            width: 860,
            padding: 30,
            backgroundColor: 'rgba(15, 23, 42, 0.92)',
            backdropFilter: 'blur(20px)',
            border: '2px solid rgba(16, 185, 129, 0.6)',
            borderRadius: 20,
            boxShadow: `0 0 45px rgba(16, 185, 129, ${glowBurst}), 0 25px 50px rgba(0, 0, 0, 0.7)`,
            transform: `scale(${prCardEntrance})`,
            opacity: prCardEntrance,
            display: 'flex',
            flexDirection: 'column',
            gap: 18,
          }}
        >
          {/* PR Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 10,
                  backgroundColor: 'rgba(16, 185, 129, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <GitPullRequest size={22} color="#10B981" />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: '#10B981', fontWeight: 700 }}>
                    PULL REQUEST #42
                  </span>
                  <span
                    style={{
                      fontFamily: theme.fonts.mono,
                      fontSize: 11,
                      padding: '2px 8px',
                      borderRadius: 4,
                      backgroundColor: 'rgba(255, 255, 255, 0.08)',
                      color: theme.colors.textSecondary,
                    }}
                  >
                    draft
                  </span>
                </div>
                <h3
                  style={{
                    margin: '4px 0 0',
                    fontFamily: theme.fonts.sans,
                    fontSize: 20,
                    fontWeight: 800,
                    color: '#FFFFFF',
                  }}
                >
                  Migrate client payment service to NexusPay v2.0
                </h3>
              </div>
            </div>

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                fontFamily: theme.fonts.mono,
                fontSize: 12,
                color: '#10B981',
                padding: '6px 14px',
                borderRadius: 8,
                backgroundColor: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.4)',
                fontWeight: 700,
              }}
            >
              <CheckCircle2 size={16} />
              ALL CHECKS PASSED
            </div>
          </div>

          {/* PR Metadata bar */}
          <div
            style={{
              padding: '12px 18px',
              backgroundColor: 'rgba(0, 0, 0, 0.4)',
              borderRadius: 10,
              border: `1px solid ${theme.colors.border}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontFamily: theme.fonts.mono,
              fontSize: 12,
              color: theme.colors.textSecondary,
            }}
          >
            <div>branch: <span style={{ color: '#06B6D4' }}>apishield/v2-repair-auto</span> ➔ <span style={{ color: '#F8FAFC' }}>main</span></div>
            <div>evidence: <span style={{ color: '#10B981' }}>Independent Pytest Passed (4/4)</span></div>
            <div>intent: <span style={{ color: '#10B981' }}>100% Preserved</span></div>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 4 }}>
            <span style={{ fontFamily: theme.fonts.sans, fontSize: 13, color: theme.colors.textMuted }}>
              Zero unreviewed code applied to production. Full audit trail preserved.
            </span>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '8px 18px',
                borderRadius: 8,
                background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                color: '#FFFFFF',
                fontFamily: theme.fonts.sans,
                fontSize: 13,
                fontWeight: 700,
                boxShadow: '0 0 15px rgba(16, 185, 129, 0.4)',
              }}
            >
              <span>Ready for Developer Review</span>
              <ArrowRight size={15} />
            </div>
          </div>
        </div>
      )}

      {/* 2. GRAND OUTRO BRANDING (Frames 60 - 120) */}
      {frame >= 50 && (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            transform: `scale(${logoReveal})`,
            opacity: logoReveal,
          }}
        >
          {/* Glowing Shield Emblem */}
          <div
            style={{
              width: 90,
              height: 90,
              borderRadius: 24,
              background: 'linear-gradient(135deg, #06B6D4 0%, #3B82F6 50%, #8B5CF6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: `0 0 60px rgba(6, 182, 212, ${glowBurst}), 0 0 100px rgba(139, 92, 246, 0.4)`,
              marginBottom: 24,
            }}
          >
            <ShieldCheck size={54} color="#FFFFFF" />
          </div>

          <h1
            style={{
              margin: '0 0 10px',
              fontFamily: theme.fonts.sans,
              fontSize: 56,
              fontWeight: 900,
              letterSpacing: '-0.03em',
              color: '#FFFFFF',
              textShadow: '0 0 40px rgba(255, 255, 255, 0.3)',
            }}
          >
            APIShield
          </h1>

          <p
            style={{
              margin: '0 0 24px',
              fontFamily: theme.fonts.sans,
              fontSize: 24,
              fontWeight: 600,
              color: '#94A3B8',
              letterSpacing: '-0.01em',
            }}
          >
            Autonomous, Intent-Aware Self-Healing API Integrations
          </p>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 16,
              fontFamily: theme.fonts.mono,
              fontSize: 13,
              color: '#06B6D4',
              padding: '8px 20px',
              borderRadius: 999,
              backgroundColor: 'rgba(6, 182, 212, 0.12)',
              border: '1px solid rgba(6, 182, 212, 0.3)',
              boxShadow: '0 0 20px rgba(6, 182, 212, 0.25)',
            }}
          >
            <span>DETECT DRIFT</span>
            <span>•</span>
            <span>MAP INTENT</span>
            <span>•</span>
            <span>ISOLATED REPAIR</span>
            <span>•</span>
            <span>VERIFIED PR</span>
          </div>
        </div>
      )}

    </AbsoluteFill>
  );
};
