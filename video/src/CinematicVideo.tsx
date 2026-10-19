import React from 'react';
import { AbsoluteFill, Sequence, interpolate, useCurrentFrame } from 'remotion';
import { NebulaBackground } from './components/NebulaBackground';
import { Scene1GatewayUpdate } from './scenes3d/Scene1GatewayUpdate';
import { Scene2ProductionDrift } from './scenes3d/Scene2ProductionDrift';
import { Scene3SemanticSentinel } from './scenes3d/Scene3SemanticSentinel';
import { Scene4SandboxHealing } from './scenes3d/Scene4SandboxHealing';
import { Scene5VerifiedPRFinale } from './scenes3d/Scene5VerifiedPRFinale';
import { Cursor } from './components/Cursor';

export const CinematicVideo: React.FC = () => {
  const frame = useCurrentFrame();

  // Screen-space cursor for Scene 1 (Gateway publish click)
  const isScene1Cursor = frame >= 20 && frame <= 115;
  const s1CursorX = interpolate(frame, [25, 68, 95], [1320, 990, 1080], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const s1CursorY = interpolate(frame, [25, 68, 95], [760, 560, 600], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const s1Clicking = frame >= 68 && frame <= 84;
  const s1Opacity = interpolate(frame, [20, 30, 105, 115], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Screen-space cursor for Scene 4 (Sandbox validation click)
  const isScene4Cursor = frame >= 445 && frame <= 535;
  const s4CursorX = interpolate(frame, [450, 490, 520], [1350, 1220, 1270], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const s4CursorY = interpolate(frame, [450, 490, 520], [680, 420, 450], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const s4Clicking = frame >= 490 && frame <= 506;
  const s4Opacity = interpolate(frame, [445, 455, 525, 535], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#08070F', overflow: 'hidden' }}>
      {/* Persistent 3D Atmospheric Nebula Glow across all scenes */}
      <NebulaBackground />

      {/* Scene 1: Gateway v2.0 Breaking Schema Update (0s - 4.6s) */}
      <Sequence from={0} durationInFrames={140}>
        <Scene1GatewayUpdate />
      </Sequence>

      {/* Scene 2: The Silent Production Breakdown (4.6s - 9.3s) */}
      <Sequence from={140} durationInFrames={140}>
        <Scene2ProductionDrift />
      </Sequence>

      {/* Scene 3: The Nightly Sentinel & Semantic Intent Graph (9.3s - 14.3s) */}
      <Sequence from={280} durationInFrames={150}>
        <Scene3SemanticSentinel />
      </Sequence>

      {/* Scene 4: Isolated Sandbox & Deterministic Healing (14.3s - 19.3s) */}
      <Sequence from={430} durationInFrames={150}>
        <Scene4SandboxHealing />
      </Sequence>

      {/* Scene 5: Automated Draft PR & APIShield Hero Finale (19.3s - 24.0s) */}
      <Sequence from={580} durationInFrames={140}>
        <Scene5VerifiedPRFinale />
      </Sequence>

      {/* Root Screen-Space Cursors (Guaranteed visible in 2D viewport above 3D planes) */}
      {isScene1Cursor && (
        <Cursor x={s1CursorX} y={s1CursorY} isClicking={s1Clicking} opacity={s1Opacity} />
      )}

      {isScene4Cursor && (
        <Cursor x={s4CursorX} y={s4CursorY} isClicking={s4Clicking} opacity={s4Opacity} />
      )}
    </AbsoluteFill>
  );
};
