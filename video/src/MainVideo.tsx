import React from 'react';
import { AbsoluteFill, Sequence, useCurrentFrame } from 'remotion';
import { Background } from './components/Background';
import { HeaderBar } from './components/HeaderBar';
import { SubtitleBar } from './components/SubtitleBar';
import { Scene1Ecosystem } from './scenes/Scene1Ecosystem';
import { Scene2BreakingDrift } from './scenes/Scene2BreakingDrift';
import { Scene3SemanticGraph } from './scenes/Scene3SemanticGraph';
import { Scene4IsolatedRepair } from './scenes/Scene4IsolatedRepair';
import { Scene5HealedPR } from './scenes/Scene5HealedPR';
import { theme } from './theme';

export const MainVideo: React.FC = () => {
  const frame = useCurrentFrame();

  // Dynamic stage state and subtitles based on active sequence
  let stage = 'ecosystem';
  let badge = '1. ECOSYSTEM ARCHITECTURE';
  let badgeColor = theme.colors.accentCyan;
  let title = 'Modern Applications Depend on Upstream API Contracts';
  let description = 'Multiple independent downstream client applications rely on provider specification v1.0.';

  if (frame >= 150 && frame < 300) {
    stage = 'drift';
    badge = '2. THE PROBLEM: SILENT SCHEMA DRIFT';
    badgeColor = theme.colors.accentRose;
    title = 'When Upstream APIs Update, Downstream Clients Break';
    description = 'Provider updates to v2.0 with breaking changes. Clients that miss the update crash in production.';
  } else if (frame >= 300 && frame < 480) {
    stage = 'detect';
    badge = '3. THE SOLUTION: SEMANTIC INTENT GRAPH';
    badgeColor = theme.colors.accentViolet;
    title = 'Continuous Monitoring & Intent-Conditioned Impact Analysis';
    description = 'Scheduled sentinel fetches contracts, runs oasdiff, and maps breaking changes to business intent.';
  } else if (frame >= 480 && frame < 630) {
    stage = 'repair';
    badge = '4. ISOLATED REPAIR & TESTING';
    badgeColor = theme.colors.accentEmerald;
    title = 'Autonomous Patch Synthesis in an Untouched Disposable Sandbox';
    description = 'Generates typed candidate patches and verifies them against independent test suites.';
  } else if (frame >= 630) {
    stage = 'healed';
    badge = '5. RECONNECTED & MERGE-READY';
    badgeColor = theme.colors.accentCyan;
    title = 'Clean GitHub Draft Pull Request Ready for Developer Review';
    description = 'Self-healing APIs: automated drift detection to validated migration PR.';
  }

  return (
    <AbsoluteFill style={{ backgroundColor: theme.colors.bgDark, fontFamily: theme.fonts.sans }}>
      {/* 1. Global Animated Ambient Cyber Background */}
      <Background />

      {/* 2. Top HUD Navigation and Telemetry Bar */}
      <HeaderBar currentStage={stage} />

      {/* 3. The 5 Choreographed Scenes */}
      <Sequence from={0} durationInFrames={150}>
        <Scene1Ecosystem />
      </Sequence>

      <Sequence from={150} durationInFrames={150}>
        <Scene2BreakingDrift />
      </Sequence>

      <Sequence from={300} durationInFrames={180}>
        <Scene3SemanticGraph />
      </Sequence>

      <Sequence from={480} durationInFrames={150}>
        <Scene4IsolatedRepair />
      </Sequence>

      <Sequence from={630} durationInFrames={120}>
        <Scene5HealedPR />
      </Sequence>

      {/* 4. Lower-Third Dynamic Kinetic Subtitle Bar */}
      <SubtitleBar
        badge={badge}
        badgeColor={badgeColor}
        title={title}
        description={description}
      />
    </AbsoluteFill>
  );
};
