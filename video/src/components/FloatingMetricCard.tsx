import React from 'react';
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { theme3d } from '../theme3d';

interface FloatingMetricCardProps {
  delay?: number;
  label: string;
  value: string;
  trend?: string;
  trendColor?: string;
  icon?: React.ReactNode;
  width?: number;
  style?: React.CSSProperties;
}

export const FloatingMetricCard: React.FC<FloatingMetricCardProps> = ({
  delay = 0,
  label,
  value,
  trend,
  trendColor = theme3d.colors.emerald,
  icon,
  width = 280,
  style = {},
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame: frame - delay,
    fps,
    config: { damping: 15, mass: 0.8, stiffness: 140 },
  });

  const floatY = Math.sin((frame + delay * 8) * 0.05) * 5;

  return (
    <div
      style={{
        width,
        padding: '14px 18px',
        borderRadius: 20,
        backgroundColor: 'rgba(20, 18, 36, 0.82)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.14)',
        boxShadow: `
          0 20px 45px rgba(0, 0, 0, 0.7),
          inset 0 1px 1px rgba(255, 255, 255, 0.25),
          0 0 25px rgba(139, 92, 246, 0.15)
        `,
        transform: `translateY(${floatY}px) scale(${entrance})`,
        opacity: entrance,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'relative',
        overflow: 'hidden',
        pointerEvents: 'none',
        boxSizing: 'border-box',
        ...style,
      }}
    >
      {/* Specular Top Border Light */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 1,
          background: 'linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.5) 50%, transparent 100%)',
        }}
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
        {icon && (
          <div
            style={{
              width: 36,
              height: 36,
              minWidth: 36,
              borderRadius: 10,
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
            }}
          >
            {icon}
          </div>
        )}
        <div style={{ minWidth: 0 }}>
          <div
            style={{
              fontFamily: theme3d.fonts.sans,
              fontSize: 11,
              fontWeight: 600,
              color: theme3d.colors.textSecondary,
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              whiteSpace: 'nowrap',
            }}
          >
            {label}
          </div>
          <div
            style={{
              fontFamily: theme3d.fonts.sans,
              fontSize: 19,
              fontWeight: 700,
              color: theme3d.colors.textPrimary,
              marginTop: 2,
              letterSpacing: '-0.02em',
              whiteSpace: 'nowrap',
            }}
          >
            {value}
          </div>
        </div>
      </div>

      {trend && (
        <div
          style={{
            fontFamily: theme3d.fonts.sans,
            fontSize: 11,
            fontWeight: 700,
            color: trendColor,
            backgroundColor: `${trendColor}1A`,
            border: `1px solid ${trendColor}33`,
            padding: '4px 8px',
            borderRadius: 8,
            whiteSpace: 'nowrap',
            marginLeft: 8,
          }}
        >
          {trend}
        </div>
      )}
    </div>
  );
};
