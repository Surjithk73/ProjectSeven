import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { MousePointer2 } from 'lucide-react';

interface CursorProps {
  x: number;
  y: number;
  isClicking?: boolean;
  opacity?: number;
}

export const Cursor: React.FC<CursorProps> = ({ x, y, isClicking = false, opacity = 1 }) => {
  const frame = useCurrentFrame();

  const clickScale = isClicking ? 0.8 : 1;
  const rippleOpacity = isClicking ? interpolate(frame % 20, [0, 20], [0.8, 0]) : 0;
  const rippleScale = isClicking ? interpolate(frame % 20, [0, 20], [0.8, 2.5]) : 1;

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: `scale(${clickScale})`,
        opacity,
        zIndex: 9999,
        pointerEvents: 'none',
      }}
    >
      {/* Click ripple wave */}
      {isClicking && (
        <div
          style={{
            position: 'absolute',
            left: 4,
            top: 4,
            width: 40,
            height: 40,
            borderRadius: '50%',
            border: '2.5px solid rgba(255, 255, 255, 0.95)',
            boxShadow: '0 0 20px rgba(255, 255, 255, 0.8)',
            transform: `translate(-50%, -50%) scale(${rippleScale})`,
            opacity: rippleOpacity,
          }}
        />
      )}

      {/* Modern White Vector Cursor (High-end Figma/SaaS style) */}
      <div
        style={{
          filter: 'drop-shadow(0 8px 18px rgba(0, 0, 0, 0.9)) drop-shadow(0 0 12px rgba(255, 255, 255, 0.6))',
        }}
      >
        <MousePointer2
          size={38}
          color="#090814"
          fill="#FFFFFF"
          strokeWidth={1.8}
        />
      </div>
    </div>
  );
};
