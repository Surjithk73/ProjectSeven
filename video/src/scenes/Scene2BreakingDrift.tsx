import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { Server, Smartphone, ShoppingCart, Truck, AlertTriangle, XCircle } from 'lucide-react';
import { theme } from '../theme';

export const Scene2BreakingDrift: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance and flash transition
  const v2Arrival = spring({
    frame: frame - 10,
    fps,
    config: { damping: 12, mass: 0.6 },
  });

  const breakShockwave = spring({
    frame: frame - 35,
    fps,
    config: { damping: 10, mass: 0.4 },
  });

  // Jitter / glitch on broken nodes
  const glitchX = breakShockwave > 0.5 ? Math.sin(frame * 1.5) * 4 : 0;
  const glitchY = breakShockwave > 0.5 ? Math.cos(frame * 1.8) * 3 : 0;

  // Red alert pulsing
  const alertPulse = interpolate(Math.sin(frame * 0.25), [-1, 1], [0.4, 0.9]);

  return (
    <AbsoluteFill style={{ padding: '120px 80px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ position: 'relative', width: 1400, height: 600 }}>
        
        {/* SVG Connecting Circuit Curves with Broken Lines */}
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
            <linearGradient id="healthyGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#10B981" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="brokenGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#F43F5E" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#F43F5E" stopOpacity="0.3" />
            </linearGradient>
          </defs>

          {/* Path 1: Client 1 (Migrated - Green/Violet) */}
          <path
            d="M 380 300 C 650 300, 700 130, 960 130"
            fill="none"
            stroke="url(#healthyGrad)"
            strokeWidth="3.5"
            strokeDasharray="4 4"
          />

          {/* Path 2: Client 2 (Broken - Red Jagged) */}
          <path
            d={
              breakShockwave > 0.5
                ? "M 380 300 Q 550 310, 640 280 L 680 330 L 720 270 L 760 310 C 840 310, 880 300, 960 300"
                : "M 380 300 C 650 300, 700 300, 960 300"
            }
            fill="none"
            stroke={breakShockwave > 0.5 ? "url(#brokenGrad)" : "rgba(244, 63, 94, 0.4)"}
            strokeWidth={breakShockwave > 0.5 ? "4" : "2"}
            strokeDasharray={breakShockwave > 0.5 ? "8 6" : "none"}
          />

          {/* Path 3: Client 3 (Broken - Red Jagged) */}
          <path
            d={
              breakShockwave > 0.5
                ? "M 380 300 Q 550 320, 640 380 L 670 420 L 710 370 L 750 430 C 840 460, 880 470, 960 470"
                : "M 380 300 C 650 300, 700 470, 960 470"
            }
            fill="none"
            stroke={breakShockwave > 0.5 ? "url(#brokenGrad)" : "rgba(244, 63, 94, 0.4)"}
            strokeWidth={breakShockwave > 0.5 ? "4" : "2"}
            strokeDasharray={breakShockwave > 0.5 ? "8 6" : "none"}
          />

          {/* Spark bursts on break lines */}
          {breakShockwave > 0.4 && (
            <g transform="translate(680, 290)">
              <circle r="18" fill="rgba(244, 63, 94, 0.3)" />
              <circle r="8" fill="#F43F5E" />
            </g>
          )}
          {breakShockwave > 0.4 && (
            <g transform="translate(670, 420)">
              <circle r="18" fill="rgba(244, 63, 94, 0.3)" />
              <circle r="8" fill="#F43F5E" />
            </g>
          )}
        </svg>

        {/* 1. API PROVIDER (Updated to v2.0 with Breaking Alert) */}
        <div
          style={{
            position: 'absolute',
            left: 20,
            top: 200,
            width: 370,
            padding: 24,
            backgroundColor: 'rgba(15, 23, 42, 0.92)',
            backdropFilter: 'blur(16px)',
            border: '2px solid rgba(139, 92, 246, 0.7)',
            borderRadius: 20,
            boxShadow: `0 0 35px rgba(139, 92, 246, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.2)`,
            transform: `scale(${v2Arrival})`,
            opacity: v2Arrival,
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
                  backgroundColor: 'rgba(139, 92, 246, 0.25)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Server size={20} color="#8B5CF6" />
              </div>
              <span style={{ fontFamily: theme.fonts.mono, fontSize: 13, color: '#8B5CF6', fontWeight: 700 }}>
                UPSTREAM UPDATE
              </span>
            </div>
            <span
              style={{
                fontFamily: theme.fonts.mono,
                fontSize: 12,
                padding: '4px 10px',
                borderRadius: 6,
                backgroundColor: 'rgba(244, 63, 94, 0.2)',
                color: '#F43F5E',
                border: '1px solid rgba(244, 63, 94, 0.5)',
                fontWeight: 800,
                letterSpacing: '0.04em',
                animation: 'pulse 1s infinite',
              }}
            >
              v2.0 BREAKING
            </span>
          </div>

          <h3
            style={{
              margin: '0 0 4px',
              fontFamily: theme.fonts.sans,
              fontSize: 22,
              fontWeight: 800,
              color: '#FFFFFF',
              letterSpacing: '-0.02em',
            }}
          >
            NexusPay Gateway
          </h3>
          <p style={{ margin: '0 0 14px', fontFamily: theme.fonts.sans, fontSize: 13, color: theme.colors.textSecondary }}>
            Published breaking contract revision
          </p>

          <div
            style={{
              padding: '12px 14px',
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              borderRadius: 8,
              border: '1px solid rgba(244, 63, 94, 0.3)',
              fontFamily: theme.fonts.mono,
              fontSize: 12,
              display: 'flex',
              flexDirection: 'column',
              gap: 6,
            }}
          >
            <div style={{ color: '#F43F5E', display: 'flex', alignItems: 'center', gap: 6 }}>
              <span>✖ DEPRECATED:</span> POST /refund
            </div>
            <div style={{ color: '#10B981', display: 'flex', alignItems: 'center', gap: 6 }}>
              <span>✚ NEW ENDPOINT:</span> POST /refunds/create
            </div>
            <div style={{ color: '#F59E0B', display: 'flex', alignItems: 'center', gap: 6 }}>
              <span>⚠ TYPE CHANGE:</span> amount: {'{value, currency}'}
            </div>
          </div>
        </div>

        {/* 2. DOWNSTREAM CLIENT APPS WITH DIVERGING FATE */}

        {/* Client 1: FinTech App (Noticed & Migrated) */}
        <div
          style={{
            position: 'absolute',
            left: 960,
            top: 60,
            width: 390,
            padding: 18,
            backgroundColor: 'rgba(15, 23, 42, 0.85)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(16, 185, 129, 0.5)',
            borderRadius: 16,
            boxShadow: '0 0 20px rgba(16, 185, 129, 0.2)',
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
                <div style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: '#10B981' }}>
                  Dev noticed docs & migrated
                </div>
              </div>
            </div>
            <div
              style={{
                fontFamily: theme.fonts.mono,
                fontSize: 11,
                color: '#10B981',
                padding: '4px 8px',
                borderRadius: 6,
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                fontWeight: 700,
              }}
            >
              MIGRATED ✓
            </div>
          </div>
        </div>

        {/* Client 2: E-Commerce Store (BROKEN - 422) */}
        <div
          style={{
            position: 'absolute',
            left: 960,
            top: 230,
            width: 390,
            padding: 18,
            backgroundColor: 'rgba(30, 15, 25, 0.9)',
            backdropFilter: 'blur(16px)',
            border: `2px solid rgba(244, 63, 94, ${alertPulse})`,
            borderRadius: 16,
            boxShadow: `0 0 35px rgba(244, 63, 94, ${alertPulse * 0.5})`,
            transform: `translate(${glitchX}px, ${glitchY}px)`,
            zIndex: 10,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 8,
                  backgroundColor: 'rgba(244, 63, 94, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <ShoppingCart size={20} color="#F43F5E" />
              </div>
              <div>
                <div style={{ fontFamily: theme.fonts.sans, fontSize: 16, fontWeight: 700, color: '#FFFFFF' }}>
                  E-Commerce Platform
                </div>
                <div style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: '#F43F5E' }}>
                  Missed update: Old v1 format
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
                color: '#F43F5E',
                padding: '4px 8px',
                borderRadius: 6,
                backgroundColor: 'rgba(244, 63, 94, 0.15)',
                border: '1px solid rgba(244, 63, 94, 0.5)',
                fontWeight: 800,
              }}
            >
              <XCircle size={14} />
              422 ERROR
            </div>
          </div>
          <div
            style={{
              padding: '6px 10px',
              backgroundColor: 'rgba(244, 63, 94, 0.12)',
              borderRadius: 6,
              fontFamily: theme.fonts.mono,
              fontSize: 11,
              color: '#FCA5A5',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            <AlertTriangle size={13} color="#F43F5E" />
            <span>CRASH: Expected amount object, got integer</span>
          </div>
        </div>

        {/* Client 3: Logistics App (BROKEN - 404 / 500) */}
        <div
          style={{
            position: 'absolute',
            left: 960,
            top: 400,
            width: 390,
            padding: 18,
            backgroundColor: 'rgba(30, 15, 25, 0.9)',
            backdropFilter: 'blur(16px)',
            border: `2px solid rgba(244, 63, 94, ${alertPulse})`,
            borderRadius: 16,
            boxShadow: `0 0 35px rgba(244, 63, 94, ${alertPulse * 0.5})`,
            transform: `translate(${glitchX * -1}px, ${glitchY * -1}px)`,
            zIndex: 10,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 8,
                  backgroundColor: 'rgba(244, 63, 94, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Truck size={20} color="#F43F5E" />
              </div>
              <div>
                <div style={{ fontFamily: theme.fonts.sans, fontSize: 16, fontWeight: 700, color: '#FFFFFF' }}>
                  Logistics & Invoicing
                </div>
                <div style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: '#F43F5E' }}>
                  Calling deleted route /refund
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
                color: '#F43F5E',
                padding: '4px 8px',
                borderRadius: 6,
                backgroundColor: 'rgba(244, 63, 94, 0.15)',
                border: '1px solid rgba(244, 63, 94, 0.5)',
                fontWeight: 800,
              }}
            >
              <XCircle size={14} />
              404 NOT FOUND
            </div>
          </div>
          <div
            style={{
              padding: '6px 10px',
              backgroundColor: 'rgba(244, 63, 94, 0.12)',
              borderRadius: 6,
              fontFamily: theme.fonts.mono,
              fontSize: 11,
              color: '#FCA5A5',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            <AlertTriangle size={13} color="#F43F5E" />
            <span>FAILURE: Route POST /refund removed in v2</span>
          </div>
        </div>

      </div>
    </AbsoluteFill>
  );
};
