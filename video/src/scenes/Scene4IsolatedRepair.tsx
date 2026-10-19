import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { Lock, FileCheck, Terminal } from 'lucide-react';
import { theme } from '../theme';

export const Scene4IsolatedRepair: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const containerEntrance = spring({
    frame: frame - 5,
    fps,
    config: { damping: 14, mass: 0.5 },
  });

  // Test suite step progression
  const test1Done = frame > 25;
  const test2Done = frame > 45;
  const test3Done = frame > 65;

  // Animated circular IPS score dial
  const dialProgress = interpolate(frame, [30, 90], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Typing effect cursor
  const cursorBlink = Math.floor(frame / 8) % 2 === 0;

  return (
    <AbsoluteFill style={{ padding: '110px 80px', display: 'flex', flexDirection: 'column', gap: 20 }}>
      
      {/* Top Banner: Disposable Sandbox Guarantee */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 24px',
          backgroundColor: 'rgba(15, 23, 42, 0.88)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          borderRadius: 14,
          boxShadow: '0 0 25px rgba(16, 185, 129, 0.18)',
          transform: `scale(${containerEntrance})`,
          opacity: containerEntrance,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div
            style={{
              width: 34,
              height: 34,
              borderRadius: 8,
              backgroundColor: 'rgba(16, 185, 129, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Lock size={18} color="#10B981" />
          </div>
          <div>
            <div style={{ fontFamily: theme.fonts.sans, fontSize: 15, fontWeight: 700, color: '#FFFFFF' }}>
              Isolated Sandbox Execution · Original Source Untouched
            </div>
            <div style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: theme.colors.accentEmerald }}>
              Temp Workspace: sha256 byte-checked · Non-blocking OS execution lock active
            </div>
          </div>
        </div>
        <div
          style={{
            fontFamily: theme.fonts.mono,
            fontSize: 12,
            color: '#10B981',
            padding: '4px 10px',
            borderRadius: 6,
            backgroundColor: 'rgba(16, 185, 129, 0.12)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            fontWeight: 700,
          }}
        >
          SAFE & DISPOSABLE
        </div>
      </div>

      {/* Main Grid: Code Diff Patch vs Verification Suite */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 480px', gap: 24, flex: 1, minHeight: 0 }}>
        
        {/* Left: Live Code Patch Generation */}
        <div
          style={{
            backgroundColor: 'rgba(11, 17, 33, 0.95)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(56, 189, 248, 0.3)',
            borderRadius: 16,
            padding: 22,
            display: 'flex',
            flexDirection: 'column',
            boxShadow: theme.glows.box,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <Terminal size={17} color="#38BDF8" />
              <span style={{ fontFamily: theme.fonts.mono, fontSize: 13, fontWeight: 700, color: '#F8FAFC' }}>
                payment_service.py · Auto-Synthesized Patch
              </span>
            </div>
            <span
              style={{
                fontFamily: theme.fonts.mono,
                fontSize: 11,
                padding: '3px 8px',
                borderRadius: 4,
                backgroundColor: 'rgba(56, 189, 248, 0.15)',
                color: '#38BDF8',
              }}
            >
              SIG-Conditioned Repair
            </span>
          </div>

          <div
            style={{
              flex: 1,
              backgroundColor: 'rgba(0, 0, 0, 0.65)',
              borderRadius: 10,
              border: `1px solid ${theme.colors.border}`,
              padding: '16px 20px',
              fontFamily: theme.fonts.mono,
              fontSize: 13,
              lineHeight: 1.7,
              display: 'flex',
              flexDirection: 'column',
              gap: 4,
              overflow: 'hidden',
            }}
          >
            <div style={{ color: theme.colors.textMuted }}>def execute_refund(charge_id: str, cents: int):</div>
            <div style={{ color: theme.colors.textMuted, paddingLeft: 20 }}>"""Preserve exact refund value and currency"""</div>
            
            {/* Old Code (Red) */}
            <div
              style={{
                backgroundColor: 'rgba(244, 63, 94, 0.18)',
                color: '#F43F5E',
                padding: '2px 8px',
                borderRadius: 4,
                marginLeft: 12,
                marginTop: 6,
              }}
            >
              - response = httpx.post(f"{'{'}API_URL{'}'}/refund", json={'{'}"amount": cents{'}'})
            </div>

            {/* New Patched Code (Green) */}
            <div
              style={{
                backgroundColor: 'rgba(16, 185, 129, 0.18)',
                color: '#10B981',
                padding: '2px 8px',
                borderRadius: 4,
                marginLeft: 12,
                marginTop: 4,
              }}
            >
              + response = httpx.post(f"{'{'}API_URL{'}'}/refunds/create", json={'{'}
            </div>
            <div
              style={{
                backgroundColor: 'rgba(16, 185, 129, 0.18)',
                color: '#10B981',
                padding: '2px 8px',
                borderRadius: 4,
                marginLeft: 28,
              }}
            >
              + &nbsp;&nbsp;&nbsp;&nbsp;"amount": {'{'}"value": cents / 100.0, "currency": "USD"{'}'},
            </div>
            <div
              style={{
                backgroundColor: 'rgba(16, 185, 129, 0.18)',
                color: '#10B981',
                padding: '2px 8px',
                borderRadius: 4,
                marginLeft: 28,
              }}
            >
              + &nbsp;&nbsp;&nbsp;&nbsp;"charge_id": charge_id
            </div>
            <div
              style={{
                backgroundColor: 'rgba(16, 185, 129, 0.18)',
                color: '#10B981',
                padding: '2px 8px',
                borderRadius: 4,
                marginLeft: 12,
              }}
            >
              + {'}'})
            </div>

            <div style={{ color: theme.colors.textMuted, paddingLeft: 20, marginTop: 8 }}>
              return response.json()
              {cursorBlink && <span style={{ color: '#06B6D4', fontWeight: 800 }}> ▌</span>}
            </div>

            {/* Patch Stats Summary */}
            <div
              style={{
                marginTop: 'auto',
                padding: '10px 14px',
                backgroundColor: 'rgba(255, 255, 255, 0.03)',
                borderRadius: 8,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: 11,
              }}
            >
              <div style={{ display: 'flex', gap: 14 }}>
                <span style={{ color: '#10B981' }}>+4 lines added</span>
                <span style={{ color: '#F43F5E' }}>-1 line removed</span>
                <span style={{ color: theme.colors.textSecondary }}>1 file modified</span>
              </div>
              <div style={{ color: '#38BDF8', fontWeight: 600 }}>
                AST Match: payment_service.py:72
              </div>
            </div>
          </div>
        </div>

        {/* Right: Independent Validation Suite & IPS Gauge */}
        <div
          style={{
            backgroundColor: 'rgba(15, 23, 42, 0.88)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(16, 185, 129, 0.35)',
            borderRadius: 16,
            padding: 22,
            display: 'flex',
            flexDirection: 'column',
            gap: 16,
            boxShadow: theme.glows.box,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <FileCheck size={18} color="#10B981" />
              <span style={{ fontFamily: theme.fonts.sans, fontSize: 15, fontWeight: 700, color: '#FFFFFF' }}>
                Independent Pytest Suite
              </span>
            </div>
            <span style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: '#10B981', fontWeight: 700 }}>
              GATED PASS
            </span>
          </div>

          {/* Test Checks */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div
              style={{
                padding: '8px 12px',
                backgroundColor: test1Done ? 'rgba(16, 185, 129, 0.12)' : 'rgba(255, 255, 255, 0.04)',
                border: test1Done ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: 8,
                fontFamily: theme.fonts.mono,
                fontSize: 11,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span style={{ color: test1Done ? '#F8FAFC' : theme.colors.textMuted }}>
                test_refund_amount_preserved
              </span>
              {test1Done ? (
                <span style={{ color: '#10B981', fontWeight: 700 }}>PASSED ✓</span>
              ) : (
                <span style={{ color: theme.colors.textMuted }}>RUNNING...</span>
              )}
            </div>

            <div
              style={{
                padding: '8px 12px',
                backgroundColor: test2Done ? 'rgba(16, 185, 129, 0.12)' : 'rgba(255, 255, 255, 0.04)',
                border: test2Done ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: 8,
                fontFamily: theme.fonts.mono,
                fontSize: 11,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span style={{ color: test2Done ? '#F8FAFC' : theme.colors.textMuted }}>
                test_currency_dollars_unwound
              </span>
              {test2Done ? (
                <span style={{ color: '#10B981', fontWeight: 700 }}>PASSED ✓</span>
              ) : (
                <span style={{ color: theme.colors.textMuted }}>QUEUED</span>
              )}
            </div>

            <div
              style={{
                padding: '8px 12px',
                backgroundColor: test3Done ? 'rgba(16, 185, 129, 0.12)' : 'rgba(255, 255, 255, 0.04)',
                border: test3Done ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: 8,
                fontFamily: theme.fonts.mono,
                fontSize: 11,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span style={{ color: test3Done ? '#F8FAFC' : theme.colors.textMuted }}>
                test_target_route_replaces_v1
              </span>
              {test3Done ? (
                <span style={{ color: '#10B981', fontWeight: 700 }}>PASSED ✓</span>
              ) : (
                <span style={{ color: theme.colors.textMuted }}>QUEUED</span>
              )}
            </div>
          </div>

          {/* Intent Preservation Score (IPS) Dial */}
          <div
            style={{
              marginTop: 'auto',
              padding: '16px',
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: 12,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ fontFamily: theme.fonts.mono, fontSize: 11, color: '#A7F3D0', fontWeight: 700 }}>
                INTENT PRESERVATION SCORE
              </div>
              <div style={{ fontFamily: theme.fonts.sans, fontSize: 13, color: theme.colors.textSecondary }}>
                Semantic Equivalence Verified
              </div>
            </div>
            <div
              style={{
                fontFamily: theme.fonts.mono,
                fontSize: 26,
                fontWeight: 900,
                color: '#10B981',
                textShadow: '0 0 15px rgba(16, 185, 129, 0.6)',
              }}
            >
              {Math.round(dialProgress)}%
            </div>
          </div>

        </div>

      </div>

    </AbsoluteFill>
  );
};
