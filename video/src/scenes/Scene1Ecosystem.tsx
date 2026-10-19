import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { Server, Smartphone, ShoppingCart, Truck, CheckCircle2 } from 'lucide-react';
import { theme } from '../theme';

export const Scene1Ecosystem: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring for Provider
  const providerEntrance = spring({
    frame: frame - 5,
    fps,
    config: { damping: 12, mass: 0.5 },
  });

  // Staggered entrance for 3 client cards
  const client1Entrance = spring({
    frame: frame - 20,
    fps,
    config: { damping: 12, mass: 0.5 },
  });
  const client2Entrance = spring({
    frame: frame - 32,
    fps,
    config: { damping: 12, mass: 0.5 },
  });
  const client3Entrance = spring({
    frame: frame - 44,
    fps,
    config: { damping: 12, mass: 0.5 },
  });

  // Animated particle offsets along the 3 streams
  const packetOffset1 = (frame * 3.5) % 100;
  const packetOffset2 = ((frame + 30) * 3.5) % 100;
  const packetOffset3 = ((frame + 60) * 3.5) % 100;

  // Pulse effect on Provider
  const providerGlow = interpolate(Math.sin(frame * 0.08), [-1, 1], [0.35, 0.7]);

  return (
    <AbsoluteFill style={{ padding: '120px 80px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ position: 'relative', width: 1400, height: 600 }}>
        
        {/* SVG Connecting Circuit Curves with Animated Data Packets */}
        <svg
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            overflow: 'visible',
            zIndex: 1,
          }}
        >
          <defs>
            <linearGradient id="streamGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#06B6D4" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#10B981" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="streamGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#06B6D4" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#3B82F6" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="streamGrad3" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#06B6D4" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0.8" />
            </linearGradient>
            <filter id="glowEffect">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Path 1: Provider -> Client 1 (Top) */}
          <path
            d="M 380 300 C 650 300, 700 130, 960 130"
            fill="none"
            stroke="url(#streamGrad1)"
            strokeWidth="3.5"
            strokeDasharray="6 6"
            opacity={client1Entrance}
          />
          {/* Path 2: Provider -> Client 2 (Middle) */}
          <path
            d="M 380 300 C 650 300, 700 300, 960 300"
            fill="none"
            stroke="url(#streamGrad2)"
            strokeWidth="3.5"
            strokeDasharray="6 6"
            opacity={client2Entrance}
          />
          {/* Path 3: Provider -> Client 3 (Bottom) */}
          <path
            d="M 380 300 C 650 300, 700 470, 960 470"
            fill="none"
            stroke="url(#streamGrad3)"
            strokeWidth="3.5"
            strokeDasharray="6 6"
            opacity={client3Entrance}
          />

          {/* Animated Glowing Packets */}
          {client1Entrance > 0.5 && (
            <circle
              cx={interpolate(packetOffset1, [0, 100], [380, 960])}
              cy={interpolate(packetOffset1, [0, 100], [300, 130])}
              r="7"
              fill="#10B981"
              filter="url(#glowEffect)"
            />
          )}
          {client2Entrance > 0.5 && (
            <circle
              cx={interpolate(packetOffset2, [0, 100], [380, 960])}
              cy={interpolate(packetOffset2, [0, 100], [300, 300])}
              r="7"
              fill="#06B6D4"
              filter="url(#glowEffect)"
            />
          )}
          {client3Entrance > 0.5 && (
            <circle
              cx={interpolate(packetOffset3, [0, 100], [380, 960])}
              cy={interpolate(packetOffset3, [0, 100], [300, 470])}
              r="7"
              fill="#8B5CF6"
              filter="url(#glowEffect)"
            />
          )}
        </svg>

        {/* 1. API PROVIDER (Left Node) */}
        <div
          style={{
            position: 'absolute',
            left: 20,
            top: 210,
            width: 360,
            padding: 24,
            backgroundColor: 'rgba(15, 23, 42, 0.88)',
            backdropFilter: 'blur(16px)',
            border: '2px solid rgba(6, 182, 212, 0.5)',
            borderRadius: 20,
            boxShadow: `0 0 35px rgba(6, 182, 212, ${providerGlow}), inset 0 1px 1px rgba(255, 255, 255, 0.2)`,
            transform: `scale(${providerEntrance})`,
            opacity: providerEntrance,
            zIndex: 10,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 8,
                  backgroundColor: 'rgba(6, 182, 212, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Server size={20} color="#06B6D4" />
              </div>
              <span style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: '#06B6D4', fontWeight: 700 }}>
                UPSTREAM SOURCE
              </span>
            </div>
            <span
              style={{
                fontFamily: theme.fonts.mono,
                fontSize: 12,
                padding: '3px 8px',
                borderRadius: 6,
                backgroundColor: 'rgba(16, 185, 129, 0.15)',
                color: '#10B981',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                fontWeight: 700,
              }}
            >
              v1.0 STABLE
            </span>
          </div>

          <h3
            style={{
              margin: '0 0 6px',
              fontFamily: theme.fonts.sans,
              fontSize: 22,
              fontWeight: 800,
              color: '#FFFFFF',
              letterSpacing: '-0.02em',
            }}
          >
            NexusPay Gateway
          </h3>
          <p style={{ margin: '0 0 16px', fontFamily: theme.fonts.sans, fontSize: 13, color: theme.colors.textSecondary }}>
            Canonical Payment Provider · OpenAPI 3.0
          </p>

          <div
            style={{
              padding: '10px 14px',
              backgroundColor: 'rgba(0, 0, 0, 0.4)',
              borderRadius: 8,
              border: `1px solid ${theme.colors.border}`,
              fontFamily: theme.fonts.mono,
              fontSize: 12,
              color: theme.colors.textSecondary,
              display: 'flex',
              flexDirection: 'column',
              gap: 4,
            }}
          >
            <div style={{ color: '#10B981' }}>✓ POST /charges</div>
            <div style={{ color: '#10B981' }}>✓ POST /refund</div>
            <div style={{ color: '#10B981' }}>✓ GET /invoices</div>
          </div>
        </div>

        {/* 2. DOWNSTREAM CLIENT APPS (Right Nodes) */}
        
        {/* Client 1: FinTech App */}
        <div
          style={{
            position: 'absolute',
            left: 960,
            top: 60,
            width: 380,
            padding: 18,
            backgroundColor: 'rgba(15, 23, 42, 0.8)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: 16,
            boxShadow: theme.glows.box,
            transform: `scale(${client1Entrance})`,
            opacity: client1Entrance,
            zIndex: 10,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 8,
                  backgroundColor: 'rgba(16, 185, 129, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Smartphone size={20} color="#10B981" />
              </div>
              <div>
                <div style={{ fontFamily: theme.fonts.sans, fontSize: 16, fontWeight: 700, color: '#FFFFFF' }}>
                  FinTech Mobile App
                </div>
                <div style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: theme.colors.textMuted }}>
                  Integration: payment_service.py
                </div>
              </div>
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 5,
                fontFamily: theme.fonts.mono,
                fontSize: 11,
                color: '#10B981',
                padding: '4px 8px',
                borderRadius: 6,
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
              }}
            >
              <CheckCircle2 size={13} />
              200 OK
            </div>
          </div>
        </div>

        {/* Client 2: E-Commerce Store */}
        <div
          style={{
            position: 'absolute',
            left: 960,
            top: 230,
            width: 380,
            padding: 18,
            backgroundColor: 'rgba(15, 23, 42, 0.8)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            borderRadius: 16,
            boxShadow: theme.glows.box,
            transform: `scale(${client2Entrance})`,
            opacity: client2Entrance,
            zIndex: 10,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 8,
                  backgroundColor: 'rgba(59, 130, 246, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <ShoppingCart size={20} color="#3B82F6" />
              </div>
              <div>
                <div style={{ fontFamily: theme.fonts.sans, fontSize: 16, fontWeight: 700, color: '#FFFFFF' }}>
                  E-Commerce Platform
                </div>
                <div style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: theme.colors.textMuted }}>
                  Integration: checkout_client.py
                </div>
              </div>
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 5,
                fontFamily: theme.fonts.mono,
                fontSize: 11,
                color: '#10B981',
                padding: '4px 8px',
                borderRadius: 6,
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
              }}
            >
              <CheckCircle2 size={13} />
              200 OK
            </div>
          </div>
        </div>

        {/* Client 3: Logistics App */}
        <div
          style={{
            position: 'absolute',
            left: 960,
            top: 400,
            width: 380,
            padding: 18,
            backgroundColor: 'rgba(15, 23, 42, 0.8)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            borderRadius: 16,
            boxShadow: theme.glows.box,
            transform: `scale(${client3Entrance})`,
            opacity: client3Entrance,
            zIndex: 10,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 8,
                  backgroundColor: 'rgba(139, 92, 246, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Truck size={20} color="#8B5CF6" />
              </div>
              <div>
                <div style={{ fontFamily: theme.fonts.sans, fontSize: 16, fontWeight: 700, color: '#FFFFFF' }}>
                  Logistics & Invoicing
                </div>
                <div style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: theme.colors.textMuted }}>
                  Integration: invoice_service.py
                </div>
              </div>
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 5,
                fontFamily: theme.fonts.mono,
                fontSize: 11,
                color: '#10B981',
                padding: '4px 8px',
                borderRadius: 6,
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
              }}
            >
              <CheckCircle2 size={13} />
              200 OK
            </div>
          </div>
        </div>

      </div>
    </AbsoluteFill>
  );
};
