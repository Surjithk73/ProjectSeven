import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { theme3d } from '../theme3d';
import { FloatingMetricCard } from '../components/FloatingMetricCard';
import { CheckCircle2, Play, Box, ShieldCheck } from 'lucide-react';

export const Scene4SandboxHealing: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 3D Camera movement
  const camRotateX = interpolate(frame, [0, 150], [16, 10]);
  const camRotateY = interpolate(frame, [0, 150], [-8, 4]);
  const camZoom = interpolate(frame, [0, 150], [0.97, 1.04]);

  // Patch Card Entrance
  const cardSpring = spring({
    frame,
    fps,
    config: { damping: 15, mass: 0.9, stiffness: 120 },
  });

  const isClicking = frame >= 60 && frame <= 76;

  // Test execution state after click
  const testsRan = frame >= 70;

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
      {/* 3D Scene */}
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
        {/* Main 3D Code Diff Glass Card */}
        <div
          style={{
            width: 720,
            padding: 34,
            borderRadius: 28,
            backgroundColor: theme3d.colors.bgCard,
            backdropFilter: 'blur(24px)',
            border: '1.5px solid rgba(255, 255, 255, 0.16)',
            boxShadow: theme3d.glow.card,
            transform: `scale(${cardSpring}) translateZ(40px)`,
            position: 'relative',
            zIndex: 10,
          }}
        >
          {/* Top highlight line */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 1,
              background: 'linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.7), transparent)',
            }}
          />

          {/* Card Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 12,
                  backgroundColor: 'rgba(16, 185, 129, 0.15)',
                  border: '1px solid rgba(16, 185, 129, 0.4)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: theme3d.colors.emerald,
                }}
              >
                <Box size={20} />
              </div>
              <div>
                <div style={{ fontFamily: theme3d.fonts.sans, fontSize: 18, fontWeight: 700, color: '#FFFFFF' }}>
                  Deterministic AST Patching
                </div>
                <div style={{ fontFamily: theme3d.fonts.mono, fontSize: 12, color: theme3d.colors.textSecondary }}>
                  isolated-sandbox-b8f9a • ephemeral container
                </div>
              </div>
            </div>

            <div
              style={{
                fontFamily: theme3d.fonts.mono,
                fontSize: 12,
                color: testsRan ? theme3d.colors.emerald : theme3d.colors.cyan,
                backgroundColor: testsRan ? `${theme3d.colors.emerald}22` : `${theme3d.colors.cyan}22`,
                border: `1px solid ${testsRan ? theme3d.colors.emerald : theme3d.colors.cyan}44`,
                padding: '8px 16px',
                borderRadius: 20,
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                transform: isClicking ? 'scale(0.95)' : 'scale(1)',
                transition: 'transform 0.1s ease',
              }}
            >
              {testsRan ? <CheckCircle2 size={14} /> : <Play size={14} />}
              {testsRan ? 'Sandbox Verified' : 'Run Sandbox Check'}
            </div>
          </div>

          {/* Code Diff Block */}
          <div
            style={{
              marginTop: 22,
              backgroundColor: 'rgba(5, 4, 10, 0.85)',
              borderRadius: 16,
              border: '1px solid rgba(255, 255, 255, 0.08)',
              padding: 20,
              fontFamily: theme3d.fonts.mono,
              fontSize: 13,
              lineHeight: 1.7,
            }}
          >
            <div style={{ color: theme3d.colors.textMuted, fontSize: 11, marginBottom: 8 }}>
              @@ src/services/billing.py:48 @@
            </div>
            <div
              style={{
                backgroundColor: 'rgba(244, 63, 94, 0.15)',
                color: '#FDA4AF',
                padding: '4px 10px',
                borderRadius: 6,
                marginBottom: 6,
              }}
            >
              - payload = &#123;"amount": order.total, "cur": order.currency&#125;
            </div>
            <div
              style={{
                backgroundColor: 'rgba(16, 185, 129, 0.15)',
                color: '#6EE7B7',
                padding: '4px 10px',
                borderRadius: 6,
              }}
            >
              + payload = &#123;"amount_in_cents": int(order.total * 100), "currency": order.currency.upper()&#125;
            </div>
          </div>

          {/* Pytest Sandbox Terminal */}
          <div
            style={{
              marginTop: 18,
              padding: '14px 18px',
              borderRadius: 14,
              backgroundColor: testsRan ? 'rgba(16, 185, 129, 0.1)' : 'rgba(0, 0, 0, 0.4)',
              border: `1px solid ${testsRan ? 'rgba(16, 185, 129, 0.4)' : 'rgba(255, 255, 255, 0.08)'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontFamily: theme3d.fonts.mono,
              fontSize: 12,
              transition: 'all 0.3s ease',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ color: testsRan ? theme3d.colors.emerald : theme3d.colors.textMuted }}>
                {testsRan ? '$ pytest tests/test_billing.py' : '$ awaiting verification...'}
              </span>
            </div>
            {testsRan && (
              <span style={{ color: theme3d.colors.emerald, fontWeight: 700 }}>
                4 passed in 0.14s (100%)
              </span>
            )}
          </div>
        </div>

        {/* Floating Metrics (Balanced placement) */}
        <FloatingMetricCard
          delay={12}
          label="Pytest Tests"
          value="4/4 Passed"
          trend="142ms"
          trendColor={theme3d.colors.emerald}
          icon={<CheckCircle2 size={18} color={theme3d.colors.emerald} />}
          style={{
            position: 'absolute',
            left: 200,
            bottom: 240,
            transform: 'translateZ(50px) rotateY(15deg)',
          }}
        />

        <FloatingMetricCard
          delay={24}
          label="Invariant Check"
          value="100% Valid"
          trend="0 Regression"
          trendColor={theme3d.colors.cyan}
          icon={<ShieldCheck size={18} color={theme3d.colors.cyan} />}
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
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5), 0 0 25px rgba(16, 185, 129, 0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}
      >
        <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: theme3d.colors.emerald }} />
        <span style={{ fontFamily: theme3d.fonts.sans, fontSize: 15, fontWeight: 600, color: '#FFFFFF' }}>
          Isolated disposable sandbox validates AST fixes against the existing test suite
        </span>
      </div>
    </AbsoluteFill>
  );
};
