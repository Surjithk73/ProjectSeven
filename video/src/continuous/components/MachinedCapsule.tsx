import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { IridescentSphere } from './IridescentSphere';
import { RollingNumber } from './RollingNumber';

interface MachinedCapsuleProps {
  progress?: number;
}

export const MachinedCapsule: React.FC<MachinedCapsuleProps> = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const entrance = spring({
    frame,
    fps,
    config: { damping: 15, mass: 0.9, stiffness: 120 },
  });

  // Tray splitting animation
  const splitSpring = spring({
    frame: frame - 12,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 100 },
  });

  const lidOffset = interpolate(splitSpring, [0, 1], [0, -110]);
  const baseOffset = interpolate(splitSpring, [0, 1], [0, 45]);

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        perspective: 1400,
        transformStyle: 'preserve-3d',
        pointerEvents: 'none',
      }}
    >
      {/* Top Rolling Version Indicator (matching ref2_02.png) */}
      <div
        style={{
          position: 'absolute',
          top: 330,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          opacity: entrance,
        }}
      >
        <div style={{ color: 'rgba(0,0,0,0.2)', fontSize: 18, fontFamily: 'monospace', fontWeight: 600 }}>
          v1.2
        </div>
        <RollingNumber
          items={['v1.2', 'v1.4', 'v2.0']}
          startFrame={5}
          durationPerItem={24}
          height={38}
          fontSize={30}
          fontWeight={700}
          color="#111111"
        />
        <div style={{ color: 'rgba(0,0,0,0.15)', fontSize: 18, fontFamily: 'monospace', fontWeight: 600 }}>
          v2.1
        </div>
      </div>

      {/* 3D Machined Aluminum Capsule Tray */}
      <div
        style={{
          position: 'relative',
          width: 240,
          height: 240,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transformStyle: 'preserve-3d',
          transform: `scale(${entrance}) rotateX(54deg) rotateZ(-28deg)`,
        }}
      >
        {/* Top Lid (Slides Upward) */}
        <div
          style={{
            position: 'absolute',
            width: 220,
            height: 140,
            borderRadius: 36,
            background: 'linear-gradient(180deg, #FDFDFD 0%, #E6E6E6 40%, #CCCCCC 100%)',
            boxShadow: `
              0 25px 50px rgba(0, 0, 0, 0.18),
              inset 0 2px 4px #FFFFFF,
              inset 0 -2px 4px rgba(0, 0, 0, 0.2)
            `,
            border: '2px solid rgba(255, 255, 255, 0.9)',
            transform: `translateY(${lidOffset}px) translateZ(50px)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {/* Inner frosted recess */}
          <div
            style={{
              width: '92%',
              height: '88%',
              borderRadius: 30,
              backgroundColor: 'rgba(255, 255, 255, 0.6)',
              boxShadow: 'inset 0 2px 6px rgba(0, 0, 0, 0.08)',
            }}
          />
        </div>

        {/* Floating Hero Iridescent Sphere in between the tray halves */}
        <div
          style={{
            position: 'absolute',
            transform: 'translateZ(25px)',
            zIndex: 10,
          }}
        >
          <IridescentSphere size={95} />
        </div>

        {/* Bottom Base (Seats with Shadow) */}
        <div
          style={{
            position: 'absolute',
            width: 220,
            height: 140,
            borderRadius: 36,
            background: 'linear-gradient(180deg, #EAEAEA 0%, #D4D4D8 50%, #A1A1AA 100%)',
            boxShadow: `
              0 30px 60px rgba(0, 0, 0, 0.25),
              inset 0 3px 5px #FFFFFF,
              inset 0 -3px 6px rgba(0, 0, 0, 0.3)
            `,
            border: '2px solid rgba(255, 255, 255, 0.85)',
            transform: `translateY(${baseOffset}px) translateZ(-30px)`,
          }}
        >
          {/* Subtle speaker/groove cut (Apple style) */}
          <div
            style={{
              position: 'absolute',
              bottom: 8,
              left: '50%',
              transform: 'translateX(-50%)',
              width: 32,
              height: 4,
              borderRadius: 4,
              backgroundColor: 'rgba(0, 0, 0, 0.2)',
            }}
          />
        </div>
      </div>

      {/* Typography Statement Below (matching ref2_02.png) */}
      <div
        style={{
          position: 'absolute',
          bottom: 330,
          textAlign: 'center',
          opacity: entrance,
        }}
      >
        <div
          style={{
            fontFamily: 'Inter, -apple-system, sans-serif',
            fontSize: 34,
            fontWeight: 500,
            color: '#111111',
            letterSpacing: '-0.03em',
          }}
        >
          No broken checkouts.
        </div>
        <div
          style={{
            fontFamily: 'Inter, -apple-system, sans-serif',
            fontSize: 22,
            fontWeight: 400,
            color: '#71717A',
            marginTop: 6,
            letterSpacing: '-0.02em',
          }}
        >
          No midnight fire drills.
        </div>
      </div>
    </div>
  );
};
