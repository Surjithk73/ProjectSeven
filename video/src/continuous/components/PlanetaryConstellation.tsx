import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface PlanetaryConstellationProps {
  progress?: number;
}

export const PlanetaryConstellation: React.FC<PlanetaryConstellationProps> = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const entrance = spring({
    frame,
    fps,
    config: { damping: 16, mass: 0.9, stiffness: 110 },
  });

  // Orbital ring rotation
  const ringRotation = frame * 0.6;

  // Diamond nodes orbiting positions (angles in radians)
  const angle1 = (ringRotation * Math.PI) / 180;
  const angle2 = ((ringRotation + 110) * Math.PI) / 180;
  const angle3 = ((ringRotation + 210) * Math.PI) / 180;
  const angle4 = ((ringRotation + 300) * Math.PI) / 180;

  const r1 = 155;
  const r2 = 195;
  const r3 = 175;
  const r4 = 215;

  const cx = 360;
  const cy = 520;

  const n1x = cx + Math.cos(angle1) * r1;
  const n1y = cy + Math.sin(angle1) * r1;

  const n2x = cx + Math.cos(angle2) * r2;
  const n2y = cy + Math.sin(angle2) * r2;

  const n3x = cx + Math.cos(angle3) * r3;
  const n3y = cy + Math.sin(angle3) * r3;

  const n4x = cx + Math.cos(angle4) * r4;
  const n4y = cy + Math.sin(angle4) * r4;

  // Wave phase for dotted lines
  const wavePhase = frame * 0.08;

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        pointerEvents: 'none',
      }}
    >
      {/* Central SVG Container for concentric orbits and constellation lines */}
      <svg
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
        }}
      >
        {/* Concentric Hairline Orbital Rings (matching ref2_04.png & ref2_06.png) */}
        <circle cx={cx} cy={cy} r="155" fill="none" stroke="rgba(0, 0, 0, 0.16)" strokeWidth="1.2" />
        <circle cx={cx} cy={cy} r="185" fill="none" stroke="rgba(0, 0, 0, 0.14)" strokeWidth="1.2" />
        <circle cx={cx} cy={cy} r="215" fill="none" stroke="rgba(0, 0, 0, 0.12)" strokeWidth="1.2" />

        {/* Dynamic Polygon Constellation Connecting Lines */}
        {frame > 15 && (
          <g opacity={interpolate(frame, [15, 30], [0, 0.85], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })}>
            <line x1={n1x} y1={n1y} x2={n2x} y2={n2y} stroke="#111111" strokeWidth="1.2" />
            <line x1={n2x} y1={n2y} x2={n3x} y2={n3y} stroke="#111111" strokeWidth="1.2" />
            <line x1={n3x} y1={n3y} x2={n4x} y2={n4y} stroke="#111111" strokeWidth="1.2" />
            <line x1={n4x} y1={n4y} x2={n1x} y2={n1y} stroke="#111111" strokeWidth="1.2" />
            <line x1={n1x} y1={n1y} x2={n3x} y2={n3y} stroke="rgba(0,0,0,0.3)" strokeWidth="1" strokeDasharray="3 3" />
          </g>
        )}

        {/* Constellation Diamond Nodes */}
        {frame > 10 && (
          <>
            {/* Node 1 */}
            <rect
              x={n1x - 4}
              y={n1y - 4}
              width="8"
              height="8"
              fill="#111111"
              transform={`rotate(45, ${n1x}, ${n1y})`}
            />
            {/* Node 2 */}
            <rect
              x={n2x - 4}
              y={n2y - 4}
              width="8"
              height="8"
              fill="#111111"
              transform={`rotate(45, ${n2x}, ${n2y})`}
            />
            {/* Node 3 */}
            <rect
              x={n3x - 4}
              y={n3y - 4}
              width="8"
              height="8"
              fill="#111111"
              transform={`rotate(45, ${n3x}, ${n3y})`}
            />
            {/* Node 4 */}
            <rect
              x={n4x - 4}
              y={n4y - 4}
              width="8"
              height="8"
              fill="#111111"
              transform={`rotate(45, ${n4x}, ${n4y})`}
            />
          </>
        )}
      </svg>

      {/* Hero Dotted Blue Planetary Sphere (matching ref2_04.png & ref2_06.png) */}
      <div
        style={{
          position: 'absolute',
          left: cx,
          top: cy,
          transform: `translate(-50%, -50%) scale(${entrance})`,
          width: 250,
          height: 250,
          borderRadius: '50%',
          background: 'radial-gradient(circle at 40% 35%, #60A5FA 0%, #2563EB 45%, #1D4ED8 80%, #1E3A8A 100%)',
          boxShadow: `
            0 25px 60px rgba(37, 99, 235, 0.35),
            inset 0 2px 4px rgba(255, 255, 255, 0.6),
            inset 0 -6px 14px rgba(15, 23, 42, 0.6)
          `,
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Curved Dotted Meridian Lines inside sphere */}
        <svg
          viewBox="0 0 250 250"
          style={{
            position: 'absolute',
            width: '100%',
            height: '100%',
          }}
        >
          {[-60, -35, -10, 15, 40, 65].map((offset, i) => {
            const shift = Math.sin(wavePhase + i * 0.8) * 6;
            return (
              <path
                key={i}
                d={`M ${125 + offset} 0 Q ${125 + offset + 35 + shift} 125 ${125 + offset} 250`}
                fill="none"
                stroke="rgba(255, 255, 255, 0.7)"
                strokeWidth="1.8"
                strokeDasharray="2 6"
              />
            );
          })}
        </svg>

        {/* Soft center specular glow */}
        <div
          style={{
            position: 'absolute',
            top: '20%',
            left: '25%',
            width: '50%',
            height: '40%',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(255, 255, 255, 0.45) 0%, transparent 65%)',
            filter: 'blur(6px)',
          }}
        />
      </div>

      {/* Typography Below Sphere (matching ref2_06.png) */}
      <div
        style={{
          position: 'absolute',
          bottom: 270,
          textAlign: 'center',
          opacity: entrance,
          maxWidth: 480,
        }}
      >
        <div
          style={{
            fontFamily: 'Inter, -apple-system, sans-serif',
            fontSize: 34,
            fontWeight: 500,
            color: '#111111',
            letterSpacing: '-0.03em',
            lineHeight: 1.25,
          }}
        >
          Full semantic intent,
        </div>
        <div
          style={{
            fontFamily: 'Inter, -apple-system, sans-serif',
            fontSize: 30,
            fontWeight: 400,
            color: '#71717A',
            letterSpacing: '-0.02em',
            marginTop: 4,
          }}
        >
          in one automated PR
        </div>
        <div
          style={{
            fontFamily: 'Inter, -apple-system, sans-serif',
            fontSize: 13,
            fontStyle: 'italic',
            fontWeight: 400,
            color: '#A1A1AA',
            marginTop: 18,
            letterSpacing: '-0.01em',
          }}
        >
          *Validated in isolated disposable sandboxes
        </div>
      </div>
    </div>
  );
};
