import React from 'react';
import {AbsoluteFill, Composition, interpolate, useCurrentFrame} from 'remotion';
import {BearJoyReel, Plan} from './BearJoyReel';
import shortPlan from '../../projects/2026-11-confidence/versions/short/timeline.json';
import fullPlan from '../../projects/2026-11-confidence/versions/full/timeline.json';
import {BearJoyReelV2, PlanV2} from './BearJoyReelV2';
import shortV2 from '../../projects/2026-11-confidence/versions/short/timeline_v2.json';
import fullV2 from '../../projects/2026-11-confidence/versions/full/timeline_v2.json';
import day24 from '../../projects/2026-11-day24-early-english/versions/main/timeline_v2.json';
import day24tight from '../../projects/2026-11-day24-early-english/versions/tight/timeline_v2.json';
import day25 from '../../projects/2026-11-day25-kyobo/versions/main/timeline_v2.json';

import {BearJoyClass, ClassPlan} from './BearJoyClass';
import day1 from '../../projects/2026-11-day1-class/versions/main/timeline.json';

import {BearJoyWelcome, WelcomePlan} from './BearJoyWelcome';
import day0 from '../../projects/2026-11-day0-welcome/versions/main/timeline.json';

import {BearJoyWelcomeReel, WelcomeReelPlan} from './BearJoyWelcomeReel';
import reelUse from '../../projects/2026-11-welcome-reels/versions/use/timeline.json';
import reelPerfect from '../../projects/2026-11-welcome-reels/versions/perfect/timeline.json';
import reelBear from '../../projects/2026-11-welcome-reels/versions/bearvoice/timeline.json';

import {BearJoyPromo, PromoPlan} from './BearJoyPromo';
import promoA from '../../projects/2026-11-day1-promos/versions/kkakkung/timeline.json';
import promoB from '../../projects/2026-11-day1-promos/versions/three-phrases/timeline.json';
import promoC from '../../projects/2026-11-day1-promos/versions/mistakes-ok/timeline.json';

const Hello: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: '#111', justifyContent: 'center', alignItems: 'center'}}>
      <h1 style={{color: 'white', fontSize: 100, opacity: interpolate(f, [0, 30], [0, 1])}}>Ready to edit</h1>
    </AbsoluteFill>
  );
};

const promo = (id: string, plan: PromoPlan) => (
  <Composition id={id} component={BearJoyPromo} durationInFrames={plan.frames} fps={30} width={1080} height={1920} defaultProps={{plan}} />
);

const wReel = (id: string, plan: WelcomeReelPlan) => (
  <Composition id={id} component={BearJoyWelcomeReel} durationInFrames={plan.frames} fps={30} width={1080} height={1920} defaultProps={{plan}} />
);

const reel = (id: string, plan: Plan) => (
  <Composition id={id} component={BearJoyReel} durationInFrames={plan.frames} fps={plan.fps} width={1080} height={1920}
    defaultProps={{plan}} />
);

const reelV2 = (id: string, plan: PlanV2) => (
  <Composition id={id} component={BearJoyReelV2} durationInFrames={plan.frames} fps={plan.fps} width={1080} height={1920}
    defaultProps={{plan}} />
);

export const Root: React.FC = () => (
  <>
    <Composition id="Hello" component={Hello} durationInFrames={60} fps={30} width={1280} height={720} />
    {reel('ConfidenceShort', shortPlan as Plan)}
    {reel('ConfidenceFull', fullPlan as Plan)}
    {reelV2('ConfidenceShortV2', shortV2 as unknown as PlanV2)}
    {reelV2('ConfidenceFullV2', fullV2 as unknown as PlanV2)}
    {reelV2('Day24', day24 as unknown as PlanV2)}
    {reelV2('Day24Tight', day24tight as unknown as PlanV2)}
    {reelV2('Day25', day25 as unknown as PlanV2)}
    {wReel('ReelUse', reelUse as unknown as WelcomeReelPlan)}
    {wReel('ReelPerfect', reelPerfect as unknown as WelcomeReelPlan)}
    {wReel('ReelBearVoice', reelBear as unknown as WelcomeReelPlan)}
    {promo('PromoKkakkung', promoA as unknown as PromoPlan)}
    {promo('PromoThreePhrases', promoB as unknown as PromoPlan)}
    {promo('PromoMistakesOk', promoC as unknown as PromoPlan)}
    <Composition id="Day1Class" component={BearJoyClass} durationInFrames={(day1 as unknown as ClassPlan).frames} fps={30} width={1920} height={1080}
      defaultProps={{plan: day1 as unknown as ClassPlan}} />
    <Composition id="Day0Welcome" component={BearJoyWelcome} durationInFrames={(day0 as unknown as WelcomePlan).frames} fps={30} width={1920} height={1080}
      defaultProps={{plan: day0 as unknown as WelcomePlan}} />
  </>
);
