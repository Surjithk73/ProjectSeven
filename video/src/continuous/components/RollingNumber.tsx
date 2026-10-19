import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { continuousTheme } from '../theme';

interface RollingNumberProps {
  items: string[];
  startFrame: number;
  durationPerItem?: number;
  height?: number;
  fontSize?: number;
  fontWeight?: number | string;
  color?: string;
  style?: React.CSSProperties;
}

export const RollingNumber: React.FC<RollingNumberProps> = ({
  items,
  startFrame,
  durationPerItem = 25,
  height = 44,
  fontSize = 32,
  fontWeight = 700,
  color = '#FFFFFF',
  style = {},
}) => {
  const frame = useCurrentFrame();
  const elapsed = Math.max(0, frame - startFrame);

  // Total progression through items
  const totalSteps = items.length - 1;
  const progress = Math.min(
    totalSteps,
    interpolate(
      elapsed,
      [0, totalSteps * durationPerItem],
      [0, totalSteps],
      {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      }
    )
  );

  const translateY = -progress * height;

  return (
    <div
      style={{
        height,
        overflow: 'hidden',
        position: 'relative',
        display: 'inline-flex',
        flexDirection: 'column',
        ...style,
      }}
    >
      <div
        style={{
          transform: `translateY(${translateY}px)`,
          transition: 'transform 0.1s linear',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {items.map((item, idx) => (
          <div
            key={idx}
            style={{
              height,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: continuousTheme.fonts.sans,
              fontSize,
              fontWeight,
              color,
              letterSpacing: '-0.03em',
              whiteSpace: 'nowrap',
            }}
          >
            {item}
          </div>
        ))}
      </div>
    </div>
  );
};
