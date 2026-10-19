import React from 'react';
import { Composition } from 'remotion';
import { ContinuousVideo } from './continuous/ContinuousVideo';
import { CinematicVideo } from './CinematicVideo';
import { MainVideo } from './MainVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Real, Continuous, Swiss/Tactile Motion Video (matching Video-92101.mp4) */}
      <Composition
        id="APIShieldContinuous"
        component={ContinuousVideo}
        durationInFrames={870}
        fps={30}
        width={720}
        height={1280}
      />
      <Composition
        id="APIShieldMotion"
        component={CinematicVideo}
        durationInFrames={720}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="APIShieldPromo"
        component={MainVideo}
        durationInFrames={750}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
