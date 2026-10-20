import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONTS} from '../style';

export const Caption: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  const opacity = interpolate(
    frame,
    [0, 10, durationInFrames - 10, durationInFrames],
    [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center'}}>
      <div
        style={{
          opacity,
          marginBottom: 60,
          maxWidth: 1500,
          backgroundColor: 'rgba(0, 0, 0, 0.75)',
          borderLeft: `6px solid ${COLORS.accent}`,
          padding: '18px 28px',
          borderRadius: 8,
          color: COLORS.text,
          fontFamily: FONTS.sans,
          fontSize: 34,
          lineHeight: 1.4,
        }}
      >
        {text.split('`').map((part, i) =>
          i % 2 === 1 ? (
            <span key={i} style={{fontFamily: FONTS.mono}}>
              {part}
            </span>
          ) : (
            <React.Fragment key={i}>{part}</React.Fragment>
          ),
        )}
      </div>
    </AbsoluteFill>
  );
};
