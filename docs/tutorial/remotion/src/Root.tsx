import React from 'react';
import {AbsoluteFill, Composition} from 'remotion';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {FPS, TRANSITION_FRAMES, shots, totalDurationFrames} from './script';
import {COLORS} from './style';
import {Caption} from './shots/Caption';
import {Intro} from './shots/Intro';
import {UploadToGitHub} from './shots/UploadToGitHub';
import {OpenDevin} from './shots/OpenDevin';
import {Footage} from './shots/Footage';
import {TypePrompt} from './shots/TypePrompt';
import {DevinTerminal} from './shots/DevinTerminal';
import {StatusTable} from './shots/StatusTable';
import {FinalSummary} from './shots/FinalSummary';
import {OutputTree} from './shots/OutputTree';
import {NestedZipFix} from './shots/NestedZipFix';
import {Outro} from './shots/Outro';
import type {Shot} from './script';

const ShotContent: React.FC<{shot: Shot}> = ({shot}) => {
  switch (shot.id) {
    case 0:
      return <Intro />;
    case 1:
      return <UploadToGitHub />;
    case 2:
      return <OpenDevin />;
    case 3:
      return <TypePrompt />;
    case 4:
      return <DevinTerminal />;
    case 5:
      return <StatusTable />;
    case 6:
      return <FinalSummary />;
    case 7:
      return <OutputTree />;
    case 8:
      return <NestedZipFix />;
    case 9:
      return <Outro />;
    default:
      return <Footage shot={shot} />;
  }
};

const BamoeMigratorTutorial: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg}}>
      <TransitionSeries>
        {shots.flatMap((shot, i) => {
          // Each incoming shot gets 15 extra frames so the 15-frame
          // cross-fades overlap without shortening the total runtime.
          const duration =
            shot.durationSec * FPS + (i > 0 ? TRANSITION_FRAMES : 0);
          const seq = (
            <TransitionSeries.Sequence
              key={`seq-${shot.id}`}
              durationInFrames={duration}
            >
              <ShotContent shot={shot} />
              <Caption text={shot.caption} />
            </TransitionSeries.Sequence>
          );
          if (i === 0) return [seq];
          return [
            <TransitionSeries.Transition
              key={`tr-${shot.id}`}
              presentation={fade()}
              timing={linearTiming({durationInFrames: TRANSITION_FRAMES})}
            />,
            seq,
          ];
        })}
      </TransitionSeries>
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => {
  return (
    <Composition
      id="BamoeMigratorTutorial"
      component={BamoeMigratorTutorial}
      durationInFrames={totalDurationFrames}
      fps={FPS}
      width={1920}
      height={1080}
    />
  );
};
