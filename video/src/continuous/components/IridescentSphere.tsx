import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';

interface IridescentSphereProps {
  size?: number;
  scale?: number;
  style?: React.CSSProperties;
}

export const IridescentSphere: React.FC<IridescentSphereProps> = ({
  size = 130,
  scale = 1,
  style = {},
}) => {
  const frame = useCurrentFrame();

  const floatY = Math.sin(frame * 0.06) * 6;
  const shadowScale = interpolate(floatY, [-6, 6], [0.88, 1.12]);
  const shadowOpacity = interpolate(floatY, [-6, 6], [0.35, 0.22]);

  return (
    <div
      style={{
        position: 'relative',
        width: size,
        height: size,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transform: `scale(${scale})`,
        ...style,
      }}
    >
      {/* Contact Drop Shadow on the studio floor (matching ref2_02.png) */}
      <div
        style={{
          position: 'absolute',
          bottom: -size * 0.32,
          left: '50%',
          transform: `translateX(-50%) scale(${shadowScale})`,
          width: size * 0.95,
          height: size * 0.32,
          borderRadius: '50%',
          background: 'radial-gradient(ellipse at center, rgba(0, 0, 0, 0.45) 0%, rgba(0, 0, 0, 0.12) 50%, transparent 75%)',
          filter: 'blur(8px)',
          opacity: shadowOpacity,
          pointerEvents: 'none',
        }}
      />

      {/* Hero Iridescent Glass/Metallic Sphere */}
      <div
        style={{
          width: size,
          height: size,
          borderRadius: '50%',
          background: 'radial-gradient(circle at 36% 30%, #C4DE45 0%, #4E9562 38%, #1E4D2F 72%, #0A1C11 100%)',
          boxShadow: `
            0 14px 30px rgba(0, 0, 0, 0.35),
            inset 0 2px 4px rgba(255, 255, 255, 0.7),
            inset 0 -6px 14px rgba(10, 28, 17, 0.8),
            0 0 20px rgba(78, 149, 98, 0.35)
          `,
          position: 'relative',
          overflow: 'hidden',
          transform: `translateY(${floatY}px)`,
        }}
      >
        {/* Specular curved gloss reflection */}
        <div
          style={{
            position: 'absolute',
            top: '10%',
            left: '20%',
            width: '60%',
            height: '35%',
            borderRadius: '50%',
            background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.85) 0%, rgba(255, 255, 255, 0) 100%)',
            filter: 'blur(1px)',
            pointerEvents: 'none',
          }}
        />

        {/* Ambient bottom rim bounce light */}
        <div
          style={{
            position: 'absolute',
            bottom: '4%',
            left: '25%',
            width: '50%',
            height: '20%',
            borderRadius: '50%',
            background: 'radial-gradient(ellipse at center, rgba(196, 222, 69, 0.4) 0%, transparent 70%)',
            filter: 'blur(4px)',
            pointerEvents: 'none',
          }}
        />
      </div>
    </div>
  );
};
