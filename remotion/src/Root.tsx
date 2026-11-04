import React from 'react';
import {AbsoluteFill, Composition, interpolate, useCurrentFrame} from 'remotion';
const Hello: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: '#111', justifyContent: 'center', alignItems: 'center'}}>
      <h1 style={{color: 'white', fontSize: 100, opacity: interpolate(f, [0, 30], [0, 1])}}>Ready to edit</h1>
    </AbsoluteFill>
  );
};
export const Root: React.FC = () => (
  <Composition id="Hello" component={Hello} durationInFrames={60} fps={30} width={1280} height={720} />
);
