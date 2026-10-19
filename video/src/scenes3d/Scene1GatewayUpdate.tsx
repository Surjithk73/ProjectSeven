import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { theme3d } from '../theme3d';
import { FloatingMetricCard } from '../components/FloatingMetricCard';
import { Server, Smartphone, ShoppingCart, Zap, ArrowRight } from 'lucide-react';

export const Scene1GatewayUpdate: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 3D Camera movement
  const camRotateX = interpolate(frame, [0, 140], [16, 12]);
  const camRotateY = interpolate(frame, [0, 140], [-10, -4]);
  const camZoom = interpolate(frame, [0, 140], [0.96, 1.04]);

  // Provider Card Entrance
  const cardSpring = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.9, stiffness: 110 },
  });

  const isClicking = frame >= 68 && frame <= 84;

  // Published state
  const isV2Published = frame >= 78;

  // Circuit line animation
  const pulseDash = (frame * 3) % 40;

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
      {/* 3D Camera Container */}
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
        {/* SVG Glowing Circuit Lines connecting cards */}
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
          {/* Line to Left Downstream App */}
          <path
            d="M 680 540 C 520 540, 480 380, 360 360"
            fill="none"
            stroke={isV2Published ? theme3d.colors.amber : theme3d.colors.violet}
            strokeWidth="2"
            strokeDasharray="6 6"
            strokeDashoffset={-pulseDash}
            opacity="0.6"
          />
          {/* Line to Right Downstream App */}
          <path
            d="M 1240 540 C 1380 540, 1420 700, 1540 720"
            fill="none"
            stroke={isV2Published ? theme3d.colors.amber : theme3d.colors.cyan}
            strokeWidth="2"
            strokeDasharray="6 6"
            strokeDashoffset={-pulseDash}
            opacity="0.6"
          />
        </svg>

        {/* Central Provider 3D Glass Card */}
        <div
          style={{
            width: 580,
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
          {/* Specular top rim highlight */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 1,
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent)',
            }}
          />

          {/* Card Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 14,
                  backgroundColor: 'rgba(139, 92, 246, 0.2)',
                  border: '1px solid rgba(139, 92, 246, 0.4)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: theme3d.colors.violet,
                }}
              >
                <Server size={22} />
              </div>
              <div>
                <div style={{ fontFamily: theme3d.fonts.sans, fontSize: 18, fontWeight: 700, color: '#FFFFFF' }}>
                  NexusPay Gateway
                </div>
                <div style={{ fontFamily: theme3d.fonts.sans, fontSize: 12, color: theme3d.colors.textSecondary }}>
                  Public API Provider • Global Payment Mesh
                </div>
              </div>
            </div>

            <div
              style={{
                fontFamily: theme3d.fonts.mono,
                fontSize: 12,
                fontWeight: 600,
                color: isV2Published ? theme3d.colors.amber : theme3d.colors.emerald,
                backgroundColor: isV2Published ? `${theme3d.colors.amber}22` : `${theme3d.colors.emerald}22`,
                border: `1px solid ${isV2Published ? theme3d.colors.amber : theme3d.colors.emerald}44`,
                padding: '6px 14px',
                borderRadius: 20,
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                transition: 'all 0.3s ease',
              }}
            >
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: isV2Published ? theme3d.colors.amber : theme3d.colors.emerald,
                  boxShadow: `0 0 10px ${isV2Published ? theme3d.colors.amber : theme3d.colors.emerald}`,
                }}
              />
              {isV2Published ? 'v2.0 Breaking Released' : 'v1.4 Live (Stable)'}
            </div>
          </div>

          {/* Active Endpoint Spec */}
          <div
            style={{
              marginTop: 22,
              padding: '16px 20px',
              backgroundColor: 'rgba(0, 0, 0, 0.45)',
              borderRadius: 16,
              border: '1px solid rgba(255, 255, 255, 0.06)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontFamily: theme3d.fonts.mono, fontSize: 13, color: theme3d.colors.textMuted }}>
                Active Schema
              </span>
              <span
                style={{
                  fontFamily: theme3d.fonts.mono,
                  fontSize: 13,
                  color: isV2Published ? theme3d.colors.amber : theme3d.colors.cyan,
                  fontWeight: 600,
                }}
              >
                {isV2Published ? 'POST /v2/payments (Breaking)' : 'POST /v1/charges'}
              </span>
            </div>
          </div>

          {/* Action Button */}
          <div
            style={{
              marginTop: 22,
              padding: '14px 24px',
              borderRadius: 14,
              background: isV2Published
                ? 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)'
                : 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)',
              boxShadow: isV2Published ? '0 10px 25px rgba(245, 158, 11, 0.4)' : '0 10px 25px rgba(139, 92, 246, 0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              transform: isClicking ? 'scale(0.96)' : 'scale(1)',
              transition: 'transform 0.1s ease',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <Zap size={18} color="#FFFFFF" />
              <span style={{ fontFamily: theme3d.fonts.sans, fontSize: 14, fontWeight: 700, color: '#FFFFFF' }}>
                {isV2Published ? 'Published to Ecosystem' : 'Publish Breaking v2.0 Update'}
              </span>
            </div>
            <ArrowRight size={18} color="#FFFFFF" />
          </div>
        </div>

        {/* Floating Downstream Consumers (Balanced inward placement) */}
        <FloatingMetricCard
          delay={12}
          label="Downstream App 1"
          value="Store Checkout"
          trend="v1.4 Client"
          trendColor={theme3d.colors.violet}
          icon={<ShoppingCart size={18} />}
          style={{
            position: 'absolute',
            left: 200,
            top: 320,
            transform: 'translateZ(25px) rotateY(14deg)',
          }}
        />

        <FloatingMetricCard
          delay={20}
          label="Downstream App 2"
          value="Mobile Subs"
          trend="v1.4 Client"
          trendColor={theme3d.colors.cyan}
          icon={<Smartphone size={18} />}
          style={{
            position: 'absolute',
            right: 200,
            bottom: 300,
            transform: 'translateZ(50px) rotateY(-14deg)',
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
          border: '1px solid rgba(255, 255, 255, 0.12)',
          padding: '12px 28px',
          borderRadius: 30,
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}
      >
        <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: theme3d.colors.violet }} />
        <span style={{ fontFamily: theme3d.fonts.sans, fontSize: 15, fontWeight: 600, color: '#FFFFFF' }}>
          Upstream API providers evolve schemas, publishing breaking changes
        </span>
      </div>
    </AbsoluteFill>
  );
};
