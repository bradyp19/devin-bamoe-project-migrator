import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONTS} from '../style';

const REPOS = [
  'my-old-java-app',
  'devin-bamoe-project-migrator',
  'random-docs-repo',
];

export const OpenDevin: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const panelIn = spring({frame, fps, config: {damping: 14}});
  const highlightAt = 50;
  const btnAt = 140;
  const btnOp = interpolate(frame, [btnAt, btnAt + 15], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const btnScale = spring({frame: frame - btnAt, fps, config: {damping: 10}});
  const glow = interpolate(frame, [btnAt + 20, btnAt + 60], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        fontFamily: FONTS.sans,
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <div style={{fontSize: 44, color: COLORS.text, marginBottom: 50}}>
        Open Devin → pick this repository
      </div>
      <div
        style={{
          transform: `scale(${panelIn})`,
          width: 900,
          backgroundColor: COLORS.panel,
          border: `1px solid ${COLORS.border}`,
          borderRadius: 12,
          padding: 16,
        }}
      >
        {REPOS.map((r, i) => {
          const isTarget = i === 1;
          const hl =
            isTarget &&
            interpolate(frame, [highlightAt, highlightAt + 12], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });
          return (
            <div
              key={r}
              style={{
                fontFamily: FONTS.mono,
                fontSize: 30,
                padding: '20px 28px',
                borderRadius: 8,
                margin: '4px 0',
                color: isTarget ? COLORS.text : COLORS.dim,
                backgroundColor: isTarget
                  ? `rgba(15, 98, 254, ${0.35 * (hl || 0)})`
                  : 'transparent',
                border: isTarget
                  ? `2px solid rgba(15, 98, 254, ${hl || 0})`
                  : '2px solid transparent',
              }}
            >
              {r}
              {isTarget && (
                <span style={{float: 'right', color: COLORS.accent}}>●</span>
              )}
            </div>
          );
        })}
      </div>
      <div
        style={{
          marginTop: 56,
          opacity: btnOp,
          transform: `scale(${btnScale})`,
          backgroundColor: COLORS.accent,
          color: COLORS.text,
          fontSize: 36,
          fontWeight: 700,
          padding: '20px 60px',
          borderRadius: 10,
          boxShadow: `0 0 ${40 * glow}px rgba(15, 98, 254, ${0.7 * glow})`,
        }}
      >
        + New session
      </div>
    </AbsoluteFill>
  );
};
