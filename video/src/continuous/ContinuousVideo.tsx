import React from 'react';
import { AbsoluteFill, Audio, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { continuousTheme } from './theme';
import { CrosshairGrid } from './components/CrosshairGrid';
import { TactileSlabs } from './components/TactileSlabs';
import { IridescentSphere } from './components/IridescentSphere';
import { MachinedCapsule } from './components/MachinedCapsule';
import { PlanetaryConstellation } from './components/PlanetaryConstellation';
import { BrandFinale } from './components/BrandFinale';

export const ContinuousVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Grand Iris Transition from Dark to Warm Studio Ivory (around frame 322 - 355)
  const irisProgress = spring({
    frame: frame - 322,
    fps,
    config: { damping: 18, mass: 1, stiffness: 85 },
  });
  const irisScale = interpolate(irisProgress, [0, 1], [0, 32]);

  // Clean, non-overlapping scene cross-fades
  const s1Opacity = interpolate(frame, [88, 98], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const s2Opacity = interpolate(frame, [100, 112, 312, 322], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const s3Opacity = interpolate(frame, [332, 345, 430, 440], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const s4Opacity = interpolate(frame, [444, 456, 560, 570], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const s5Opacity = interpolate(frame, [574, 586, 732, 742], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const s6Opacity = interpolate(frame, [746, 758], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // Camera subtle breathing pan across the whole video
  const camPanY = Math.sin(frame * 0.02) * 8;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: continuousTheme.colors.darkBg,
        overflow: 'hidden',
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
      }}
    >
      {/* Import Inter Font */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
      `}</style>

      {/* Synchronized Studio Voiceover Track */}
      <Audio src={staticFile('voiceover.mp3')} volume={1} />

      {/* --- ACT 1: DARK STUDIO (0 - 11s / frames 0 - 325) --- */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `translateY(${camPanY}px)`,
        }}
      >
        {/* Scene 1: Crosshair Grid Hook (0 - 3.3s / frames 0 - 100) */}
        {frame < 100 && (
          <div style={{ position: 'absolute', inset: 0, opacity: s1Opacity }}>
            <CrosshairGrid />
            {/* Opening Kinetic Typography */}
            <div
              style={{
                position: 'absolute',
                top: 280,
                left: '50%',
                transform: 'translateX(-50%)',
                textAlign: 'center',
                width: '85%',
              }}
            >
              <div
                style={{
                  fontFamily: 'Inter, -apple-system, sans-serif',
                  fontSize: 34,
                  fontWeight: 500,
                  color: '#FFFFFF',
                  letterSpacing: '-0.03em',
                  lineHeight: 1.25,
                }}
              >
                What happens when APIs change?
              </div>
            </div>
          </div>
        )}

        {/* Scene 2: Tactile Isometric Slabs & Stacking Costs (3.3 - 10.8s / frames 100 - 325) */}
        {frame >= 99 && frame < 326 && (
          <div style={{ position: 'absolute', inset: 0, opacity: s2Opacity }}>
            <TactileSlabs />
            {/* Typography Statement */}
            <div
              style={{
                position: 'absolute',
                top: 260,
                left: '50%',
                transform: 'translateX(-50%)',
                textAlign: 'center',
                width: '85%',
              }}
            >
              <div
                style={{
                  fontFamily: 'Inter, -apple-system, sans-serif',
                  fontSize: 32,
                  fontWeight: 500,
                  color: '#FFFFFF',
                  letterSpacing: '-0.03em',
                  lineHeight: 1.3,
                }}
              >
                {frame < 185 ? (
                  <span>Well usually, it hurts.</span>
                ) : (
                  <span>A silent v2 update, stacked 422 errors...</span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* --- EXPANDING LUMINOUS WARM STUDIO IRIS TRANSITION (matching ref_12.png) --- */}
      {frame >= 320 && (
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: '50%',
            width: 100,
            height: 100,
            borderRadius: '50%',
            backgroundColor: continuousTheme.colors.lightBg,
            transform: `translate(-50%, -50%) scale(${irisScale})`,
            pointerEvents: 'none',
            zIndex: 30,
            boxShadow: '0 0 120px rgba(247, 247, 245, 0.8)',
          }}
        />
      )}

      {/* --- ACT 2 & 3 & 4: WARM STUDIO IVORY (11s - 29s / frames 330 - 870) --- */}
      {frame >= 330 && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            zIndex: 40,
            backgroundColor: frame > 355 ? continuousTheme.colors.lightBg : 'transparent',
            transform: `translateY(${camPanY * 0.7}px)`,
          }}
        >
          {/* Scene 3: Contrast Shift & Simpler Statement (11 - 14.7s / frames 330 - 442) */}
          {frame < 442 && (
            <div
              style={{
                position: 'absolute',
                inset: 0,
                opacity: s3Opacity,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <div style={{ marginBottom: 40 }}>
                <IridescentSphere size={140} />
              </div>

              <div style={{ textAlign: 'center', width: '85%' }}>
                <div
                  style={{
                    fontFamily: 'Inter, -apple-system, sans-serif',
                    fontSize: 36,
                    fontWeight: 600,
                    color: '#111111',
                    letterSpacing: '-0.03em',
                    lineHeight: 1.25,
                  }}
                >
                  APIShield is simpler than that.
                </div>
                <div
                  style={{
                    fontFamily: 'Inter, -apple-system, sans-serif',
                    fontSize: 22,
                    fontWeight: 400,
                    color: '#71717A',
                    letterSpacing: '-0.02em',
                    marginTop: 10,
                  }}
                >
                  Continuous contract healing.
                </div>
              </div>
            </div>
          )}

          {/* Scene 4: Machined Hardware Capsule Tray (14.8 - 19s / frames 443 - 572) */}
          {frame >= 443 && frame < 572 && (
            <div style={{ position: 'absolute', inset: 0, opacity: s4Opacity }}>
              <MachinedCapsule />
            </div>
          )}

          {/* Scene 5: Dotted Planetary Constellation (19.1 - 24.7s / frames 573 - 744) */}
          {frame >= 573 && frame < 744 && (
            <div style={{ position: 'absolute', inset: 0, opacity: s5Opacity }}>
              <PlanetaryConstellation />
            </div>
          )}

          {/* Scene 6: Brand Finale & Tactile CTA Button (24.8 - 29s / frames 745 - 870) */}
          {frame >= 745 && (
            <div style={{ position: 'absolute', inset: 0, opacity: s6Opacity }}>
              <BrandFinale />
            </div>
          )}
        </div>
      )}
    </AbsoluteFill>
  );
};
