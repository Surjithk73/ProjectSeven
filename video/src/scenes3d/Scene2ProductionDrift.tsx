import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { theme3d } from '../theme3d';
import { FloatingMetricCard } from '../components/FloatingMetricCard';
import { AlertTriangle, XCircle, TrendingDown, Flame } from 'lucide-react';

export const Scene2ProductionDrift: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 3D Camera drift
  const camRotateX = interpolate(frame, [0, 140], [20, 14]);
  const camRotateY = interpolate(frame, [0, 140], [8, 2]);
  const camZoom = interpolate(frame, [0, 140], [1, 1.07]);

  // Entrance spring
  const errorCardSpring = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.8, stiffness: 130 },
  });

  // Dramatic shake on failure trigger
  const shakeX = frame > 20 && frame < 55 ? Math.sin(frame * 1.6) * 5 * Math.exp(-(frame - 20) / 18) : 0;
  const shakeY = frame > 20 && frame < 55 ? Math.cos(frame * 1.7) * 4 * Math.exp(-(frame - 20) / 18) : 0;

  // Pulse intensity for warning glow
  const redPulse = 0.55 + Math.sin(frame * 0.18) * 0.35;
  const errorDash = (frame * 4) % 30;

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
      {/* 3D Container */}
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transform: `scale(${camZoom}) rotateX(${camRotateX}deg) rotateY(${camRotateY}deg) translate(${shakeX}px, ${shakeY}px)`,
          transformStyle: 'preserve-3d',
          position: 'relative',
        }}
      >
        {/* SVG Broken Circuit Lines */}
        <svg
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none',
            zIndex: 1,
          }}
        >
          <path
            d="M 660 540 C 520 540, 480 340, 360 320"
            fill="none"
            stroke={theme3d.colors.rose}
            strokeWidth="2.5"
            strokeDasharray="8 6"
            strokeDashoffset={errorDash}
            opacity="0.8"
          />
          <path
            d="M 1260 540 C 1380 540, 1420 720, 1540 740"
            fill="none"
            stroke={theme3d.colors.rose}
            strokeWidth="2.5"
            strokeDasharray="8 6"
            strokeDashoffset={errorDash}
            opacity="0.8"
          />
        </svg>

        {/* Central 3D Glass Error Card */}
        <div
          style={{
            width: 620,
            padding: 36,
            borderRadius: 28,
            backgroundColor: 'rgba(28, 14, 24, 0.85)',
            backdropFilter: 'blur(24px)',
            border: `1.5px solid rgba(244, 63, 94, ${redPulse})`,
            boxShadow: `
              0 30px 70px rgba(0, 0, 0, 0.8),
              0 0 60px rgba(244, 63, 94, ${redPulse * 0.7}),
              inset 0 1px 2px rgba(255, 255, 255, 0.4)
            `,
            transform: `scale(${errorCardSpring}) translateZ(50px)`,
            position: 'relative',
            zIndex: 10,
          }}
        >
          {/* Top Rose Rim Highlight */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 2,
              background: 'linear-gradient(90deg, transparent, #F43F5E, transparent)',
            }}
          />

          {/* Header with Error Badge */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: 16,
                  backgroundColor: 'rgba(244, 63, 94, 0.2)',
                  border: '1px solid rgba(244, 63, 94, 0.5)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: theme3d.colors.rose,
                }}
              >
                <AlertTriangle size={24} />
              </div>
              <div>
                <div style={{ fontFamily: theme3d.fonts.sans, fontSize: 20, fontWeight: 700, color: '#FFFFFF' }}>
                  422 Unprocessable Content
                </div>
                <div style={{ fontFamily: theme3d.fonts.sans, fontSize: 13, color: theme3d.colors.rose }}>
                  Upstream Contract Violation • Production Failure
                </div>
              </div>
            </div>

            <div
              style={{
                fontFamily: theme3d.fonts.mono,
                fontSize: 12,
                fontWeight: 700,
                color: '#FFFFFF',
                backgroundColor: theme3d.colors.rose,
                padding: '6px 14px',
                borderRadius: 20,
                boxShadow: '0 0 20px rgba(244, 63, 94, 0.6)',
              }}
            >
              SILENT CRASH
            </div>
          </div>

          {/* Schema Mismatch Breakdown */}
          <div
            style={{
              marginTop: 24,
              padding: 20,
              borderRadius: 18,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              fontFamily: theme3d.fonts.mono,
              fontSize: 13,
              display: 'flex',
              flexDirection: 'column',
              gap: 12,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ color: theme3d.colors.textSecondary }}>v2 Required:</span>
              <span style={{ color: theme3d.colors.emerald }}>"amount_in_cents" (integer)</span>
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingTop: 8,
                borderTop: '1px solid rgba(255,255,255,0.06)',
              }}
            >
              <span style={{ color: theme3d.colors.textSecondary }}>Client Sent:</span>
              <span style={{ color: theme3d.colors.rose }}>"amount": 49.99 (missing field!)</span>
            </div>
          </div>

          {/* Impact Status Banner */}
          <div
            style={{
              marginTop: 20,
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              color: theme3d.colors.textSecondary,
              fontSize: 13,
              fontFamily: theme3d.fonts.sans,
            }}
          >
            <XCircle size={16} color={theme3d.colors.rose} />
            <span>Downstream checkout flow blocked for active users</span>
          </div>
        </div>

        {/* Floating Red Warning Metric Cards */}
        <FloatingMetricCard
          delay={10}
          label="Payment Drops"
          value="100% Failed"
          trend="+184 Errors"
          trendColor={theme3d.colors.rose}
          icon={<TrendingDown size={18} color={theme3d.colors.rose} />}
          style={{
            position: 'absolute',
            left: 190,
            top: 260,
            transform: 'translateZ(30px) rotateY(16deg)',
          }}
        />

        <FloatingMetricCard
          delay={22}
          label="Human Alert"
          value="Undetected"
          trend="No Tests Caught"
          trendColor={theme3d.colors.amber}
          icon={<Flame size={18} color={theme3d.colors.amber} />}
          style={{
            position: 'absolute',
            right: 190,
            bottom: 260,
            transform: 'translateZ(60px) rotateY(-16deg)',
          }}
        />
      </div>

      {/* Subtitle Pill */}
      <div
        style={{
          position: 'absolute',
          bottom: 48,
          backgroundColor: 'rgba(28, 14, 24, 0.85)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(244, 63, 94, 0.4)',
          padding: '12px 28px',
          borderRadius: 30,
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(244, 63, 94, 0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}
      >
        <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: theme3d.colors.rose }} />
        <span style={{ fontFamily: theme3d.fonts.sans, fontSize: 15, fontWeight: 600, color: '#FFFFFF' }}>
          Unannounced schema changes cause silent production outages & lost revenue
        </span>
      </div>
    </AbsoluteFill>
  );
};
