import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { ShieldCheck, Activity } from 'lucide-react';
import { theme } from '../theme';

interface HeaderBarProps {
  currentStage: string;
}

export const HeaderBar: React.FC<HeaderBarProps> = ({ currentStage }) => {
  const frame = useCurrentFrame();

  const stages = [
    { id: 'ecosystem', label: '1. CONNECTIVITY' },
    { id: 'drift', label: '2. BREAKING DRIFT' },
    { id: 'detect', label: '3. INTENT GRAPH' },
    { id: 'repair', label: '4. ISOLATED REPAIR' },
    { id: 'healed', label: '5. SELF-HEALED' },
  ];

  const pulse = interpolate(Math.sin(frame * 0.1), [-1, 1], [0.6, 1]);

  return (
    <div
      style={{
        position: 'absolute',
        top: 36,
        left: 64,
        right: 64,
        height: 64,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 28px',
        backgroundColor: 'rgba(15, 23, 42, 0.65)',
        backdropFilter: 'blur(16px)',
        border: `1px solid ${theme.colors.border}`,
        borderRadius: 16,
        boxShadow: theme.glows.box,
        zIndex: 50,
      }}
    >
      {/* Brand logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <div
          style={{
            width: 38,
            height: 38,
            borderRadius: 10,
            background: 'linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(6, 182, 212, 0.5)',
          }}
        >
          <ShieldCheck size={22} color="#FFFFFF" />
        </div>
        <div>
          <div
            style={{
              fontFamily: theme.fonts.sans,
              fontSize: 20,
              fontWeight: 800,
              letterSpacing: '-0.02em',
              color: theme.colors.textPrimary,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            APIShield
            <span
              style={{
                fontSize: 10,
                fontWeight: 700,
                padding: '2px 6px',
                borderRadius: 4,
                backgroundColor: 'rgba(6, 182, 212, 0.15)',
                color: theme.colors.accentCyan,
                border: '1px solid rgba(6, 182, 212, 0.3)',
                letterSpacing: '0.05em',
              }}
            >
              AUTONOMOUS ENGINE
            </span>
          </div>
        </div>
      </div>

      {/* Stage Flow Pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {stages.map((st) => {
          const isActive = st.id === currentStage;
          return (
            <div
              key={st.id}
              style={{
                fontFamily: theme.fonts.mono,
                fontSize: 12,
                fontWeight: isActive ? 700 : 500,
                padding: '6px 14px',
                borderRadius: 8,
                backgroundColor: isActive
                  ? 'rgba(56, 189, 248, 0.18)'
                  : 'rgba(255, 255, 255, 0.03)',
                color: isActive ? theme.colors.accentCyan : theme.colors.textMuted,
                border: isActive
                  ? '1px solid rgba(56, 189, 248, 0.45)'
                  : '1px solid transparent',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              {isActive && (
                <span
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    backgroundColor: theme.colors.accentCyan,
                    boxShadow: '0 0 8px #06B6D4',
                  }}
                />
              )}
              {st.label}
            </div>
          );
        })}
      </div>

      {/* Live System Telemetry */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            fontFamily: theme.fonts.mono,
            fontSize: 12,
            color: theme.colors.textSecondary,
          }}
        >
          <Activity size={14} color={theme.colors.accentEmerald} style={{ opacity: pulse }} />
          <span>FPS 30 · HD 1080p</span>
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '4px 10px',
            borderRadius: 6,
            backgroundColor: 'rgba(16, 185, 129, 0.12)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            fontFamily: theme.fonts.mono,
            fontSize: 11,
            fontWeight: 600,
            color: theme.colors.accentEmerald,
          }}
        >
          <span>ACTIVE</span>
        </div>
      </div>
    </div>
  );
};
