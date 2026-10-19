import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { theme } from '../theme';

interface SubtitleBarProps {
  badge: string;
  badgeColor?: string;
  title: string;
  description: string;
}

export const SubtitleBar: React.FC<SubtitleBarProps> = ({
  badge,
  badgeColor = theme.colors.accentCyan,
  title,
  description,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.6 },
  });

  const translateY = interpolate(entrance, [0, 1], [40, 0]);
  const opacity = interpolate(entrance, [0, 1], [0, 1]);

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 40,
        left: 64,
        right: 64,
        height: 84,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 32px',
        backgroundColor: 'rgba(15, 23, 42, 0.78)',
        backdropFilter: 'blur(20px)',
        border: `1px solid ${theme.colors.border}`,
        borderRadius: 16,
        boxShadow: theme.glows.box,
        transform: `translateY(${translateY}px)`,
        opacity,
        zIndex: 50,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
        <span
          style={{
            fontFamily: theme.fonts.mono,
            fontSize: 11,
            fontWeight: 800,
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            padding: '6px 12px',
            borderRadius: 8,
            backgroundColor: `${badgeColor}22`,
            color: badgeColor,
            border: `1px solid ${badgeColor}55`,
            boxShadow: `0 0 12px ${badgeColor}33`,
          }}
        >
          {badge}
        </span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <div
            style={{
              fontFamily: theme.fonts.sans,
              fontSize: 18,
              fontWeight: 700,
              color: theme.colors.textPrimary,
              letterSpacing: '-0.01em',
            }}
          >
            {title}
          </div>
          <div
            style={{
              fontFamily: theme.fonts.sans,
              fontSize: 14,
              color: theme.colors.textSecondary,
            }}
          >
            {description}
          </div>
        </div>
      </div>

      <div
        style={{
          fontFamily: theme.fonts.mono,
          fontSize: 11,
          color: theme.colors.textMuted,
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}
      >
        <span>STATUS:</span>
        <span style={{ color: badgeColor, fontWeight: 700 }}>SYNCHRONIZED</span>
      </div>
    </div>
  );
};
