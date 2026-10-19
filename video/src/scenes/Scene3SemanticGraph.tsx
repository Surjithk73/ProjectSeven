import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { Clock, GitCompare, Sparkles, Network } from 'lucide-react';
import { theme } from '../theme';

export const Scene3SemanticGraph: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const sentinelEntrance = spring({
    frame: frame - 5,
    fps,
    config: { damping: 14, mass: 0.5 },
  });

  const diffEntrance = spring({
    frame: frame - 20,
    fps,
    config: { damping: 12, mass: 0.5 },
  });

  const sigEntrance = spring({
    frame: frame - 40,
    fps,
    config: { damping: 12, mass: 0.5 },
  });

  // Animated glow pulse on graph nodes
  const nodeGlow = interpolate(Math.sin(frame * 0.12), [-1, 1], [0.3, 0.7]);
  const scanSweep = interpolate((frame * 2) % 100, [0, 100], [-100, 450]);

  return (
    <AbsoluteFill style={{ padding: '110px 80px', display: 'flex', flexDirection: 'column', gap: 24 }}>
      
      {/* Top Banner: Nightly Scheduled Trigger Sentinel */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 24px',
          backgroundColor: 'rgba(15, 23, 42, 0.85)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(6, 182, 212, 0.4)',
          borderRadius: 14,
          boxShadow: '0 0 25px rgba(6, 182, 212, 0.2)',
          transform: `scale(${sentinelEntrance})`,
          opacity: sentinelEntrance,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div
            style={{
              width: 34,
              height: 34,
              borderRadius: 8,
              backgroundColor: 'rgba(6, 182, 212, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Clock size={18} color="#06B6D4" />
          </div>
          <div>
            <div style={{ fontFamily: theme.fonts.sans, fontSize: 15, fontWeight: 700, color: '#FFFFFF' }}>
              Scheduled Sentinel: Continuous API Drift Detection
            </div>
            <div style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: theme.colors.accentCyan }}>
              cron: 02:00 AM Polling · Fetched upstream OpenAPI v2.0 spec
            </div>
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
            padding: '5px 12px',
            borderRadius: 8,
            backgroundColor: 'rgba(16, 185, 129, 0.12)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            fontWeight: 700,
          }}
        >
          <Sparkles size={14} />
          DRIFT DETECTED: 2 BREAKING CHANGES
        </div>
      </div>

      {/* Main Grid: Left (oasdiff Terminal) vs Right (Semantic Intent Graph) */}
      <div style={{ display: 'grid', gridTemplateColumns: '520px 1fr', gap: 28, flex: 1, minHeight: 0 }}>
        
        {/* LEFT: oasdiff Contract Comparison Terminal */}
        <div
          style={{
            backgroundColor: 'rgba(11, 17, 33, 0.9)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(56, 189, 248, 0.3)',
            borderRadius: 16,
            padding: 22,
            display: 'flex',
            flexDirection: 'column',
            boxShadow: theme.glows.box,
            transform: `scale(${diffEntrance})`,
            opacity: diffEntrance,
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Subtle scanner sweep line */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              top: `${scanSweep}px`,
              height: 2,
              background: 'linear-gradient(90deg, transparent, #06B6D4, transparent)',
              boxShadow: '0 0 10px #06B6D4',
              opacity: 0.6,
            }}
          />

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <GitCompare size={17} color="#38BDF8" />
              <span style={{ fontFamily: theme.fonts.mono, fontSize: 13, fontWeight: 700, color: '#F8FAFC' }}>
                oasdiff Contract Differ
              </span>
            </div>
            <span style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: theme.colors.textMuted }}>
              v1.0 ➔ v2.0
            </span>
          </div>

          <div
            style={{
              backgroundColor: 'rgba(0, 0, 0, 0.6)',
              borderRadius: 10,
              border: `1px solid ${theme.colors.border}`,
              padding: 16,
              fontFamily: theme.fonts.mono,
              fontSize: 12,
              lineHeight: 1.6,
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              gap: 8,
            }}
          >
            <div style={{ color: theme.colors.textMuted, fontSize: 11, borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: 6 }}>
              ## Breaking Changes Detected (AST Mapped):
            </div>

            <div style={{ backgroundColor: 'rgba(244, 63, 94, 0.15)', padding: '6px 10px', borderRadius: 6, color: '#F43F5E' }}>
              - paths: POST /refund (removed)
            </div>
            <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', padding: '6px 10px', borderRadius: 6, color: '#10B981' }}>
              + paths: POST /refunds/create (added)
            </div>

            <div style={{ height: 4 }} />

            <div style={{ backgroundColor: 'rgba(244, 63, 94, 0.15)', padding: '6px 10px', borderRadius: 6, color: '#F43F5E' }}>
              - schema.properties.amount: int (cents)
            </div>
            <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', padding: '6px 10px', borderRadius: 6, color: '#10B981' }}>
              + schema.properties.amount: {'{ value: float, currency: str }'}
            </div>

            <div style={{ marginTop: 'auto', paddingTop: 8, borderTop: '1px solid rgba(255,255,255,0.08)', color: '#06B6D4', fontSize: 11 }}>
              &gt; Localization: 2 call sites affected in payment_service.py
            </div>
          </div>
        </div>

        {/* RIGHT: The Semantic Intent Graph (SIG) Visualizer */}
        <div
          style={{
            backgroundColor: 'rgba(15, 23, 42, 0.85)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(139, 92, 246, 0.4)',
            borderRadius: 16,
            padding: 24,
            display: 'flex',
            flexDirection: 'column',
            boxShadow: theme.glows.box,
            transform: `scale(${sigEntrance})`,
            opacity: sigEntrance,
            position: 'relative',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  backgroundColor: 'rgba(139, 92, 246, 0.25)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Network size={18} color="#8B5CF6" />
              </div>
              <div>
                <span style={{ fontFamily: theme.fonts.sans, fontSize: 16, fontWeight: 800, color: '#FFFFFF' }}>
                  Semantic Intent Graph (SIG)
                </span>
                <span style={{ marginLeft: 8, fontFamily: theme.fonts.mono, fontSize: 11, color: '#A78BFA' }}>
                  Property Graph Knowledge Base
                </span>
              </div>
            </div>
            <span
              style={{
                fontFamily: theme.fonts.mono,
                fontSize: 11,
                padding: '4px 10px',
                borderRadius: 6,
                backgroundColor: 'rgba(139, 92, 246, 0.15)',
                color: '#C4B5FD',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                fontWeight: 700,
              }}
            >
              RESOLVED CONSTRAINTS
            </span>
          </div>

          {/* Connected Graph Flow: Endpoint -> AST Call Site -> Intent -> Test */}
          <div
            style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-around',
              position: 'relative',
              padding: '10px 18px',
            }}
          >
            {/* SVG Connecting Flow Lines */}
            <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible', zIndex: 1 }}>
              <line x1="36" y1="50" x2="36" y2="105" stroke="#8B5CF6" strokeWidth="2.5" strokeDasharray="4 4" />
              <line x1="36" y1="150" x2="36" y2="205" stroke="#06B6D4" strokeWidth="2.5" strokeDasharray="4 4" />
              <line x1="36" y1="250" x2="36" y2="305" stroke="#10B981" strokeWidth="2.5" strokeDasharray="4 4" />
            </svg>

            {/* Node 1: API Endpoint */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 16,
                padding: '12px 18px',
                backgroundColor: 'rgba(139, 92, 246, 0.15)',
                border: '1px solid rgba(139, 92, 246, 0.5)',
                borderRadius: 12,
                boxShadow: `0 0 20px rgba(139, 92, 246, ${nodeGlow})`,
                zIndex: 2,
              }}
            >
              <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: '#8B5CF6', boxShadow: '0 0 8px #8B5CF6' }} />
              <div>
                <span style={{ fontFamily: theme.fonts.mono, fontSize: 10, color: '#A78BFA', fontWeight: 700, textTransform: 'uppercase' }}>
                  CHANGED CONTRACT ENDPOINT
                </span>
                <div style={{ fontFamily: theme.fonts.mono, fontSize: 13, fontWeight: 700, color: '#FFFFFF' }}>
                  POST /refunds/create {'(was /refund)'}
                </div>
              </div>
            </div>

            {/* Node 2: AST Client Call Site */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 16,
                padding: '12px 18px',
                backgroundColor: 'rgba(6, 182, 212, 0.12)',
                border: '1px solid rgba(6, 182, 212, 0.45)',
                borderRadius: 12,
                boxShadow: `0 0 20px rgba(6, 182, 212, ${nodeGlow})`,
                zIndex: 2,
              }}
            >
              <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: '#06B6D4', boxShadow: '0 0 8px #06B6D4' }} />
              <div>
                <span style={{ fontFamily: theme.fonts.mono, fontSize: 10, color: '#67E8F9', fontWeight: 700, textTransform: 'uppercase' }}>
                  CONSUMING CLIENT AST CALL-SITE
                </span>
                <div style={{ fontFamily: theme.fonts.mono, fontSize: 13, fontWeight: 700, color: '#FFFFFF' }}>
                  payment_service.py:72 :: execute_refund()
                </div>
              </div>
            </div>

            {/* Node 3: Inferred Business Intent */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 16,
                padding: '12px 18px',
                backgroundColor: 'rgba(16, 185, 129, 0.12)',
                border: '1px solid rgba(16, 185, 129, 0.45)',
                borderRadius: 12,
                boxShadow: `0 0 20px rgba(16, 185, 129, ${nodeGlow})`,
                zIndex: 2,
              }}
            >
              <div style={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: '#10B981', boxShadow: '0 0 8px #10B981' }} />
              <div>
                <span style={{ fontFamily: theme.fonts.mono, fontSize: 10, color: '#6EE7B7', fontWeight: 700, textTransform: 'uppercase' }}>
                  DEVELOPER-CONFIRMED BUSINESS INTENT
                </span>
                <div style={{ fontFamily: theme.fonts.sans, fontSize: 13, fontWeight: 700, color: '#FFFFFF' }}>
                  "Preserve exact refund value and currency integrity without unit conversion loss"
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>

    </AbsoluteFill>
  );
};
