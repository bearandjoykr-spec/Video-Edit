import React from 'react';
import {Composition} from 'remotion';
import {TemplarEpisode, TemplarPlan} from './TemplarEpisode';
import demo from '../../../projects/2026-11-templar-ep01-genesis1/versions/demo/plan.json';
import ep01 from '../../../projects/2026-11-templar-ep01-genesis1/versions/main/plan.json';

const comp = (id: string, plan: TemplarPlan) => (
  <Composition key={id} id={id} component={TemplarEpisode as any} durationInFrames={Math.ceil(plan.duration * plan.fps)}
    fps={plan.fps} width={1920} height={1080} defaultProps={{plan}} />
);

export const TemplarRoot: React.FC = () => <>{comp('TemplarDemo', demo as TemplarPlan)}{comp('TemplarEp01', ep01 as unknown as TemplarPlan)}</>;
