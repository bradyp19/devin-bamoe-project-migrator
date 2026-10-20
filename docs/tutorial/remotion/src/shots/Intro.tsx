import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONTS} from '../style';

const STEPS = [
  '1. Put your v8 project folder (or .zip) into  v8-projects/',
  '2. Open Devin on the web → choose this repository → New session',
  '3. Type:   Migrate my project',
];

const TypedLine: React.FC<{line: string; start: number}> = ({line, start}) => {
  const frame = useCurrentFrame();
  const chars = Math.max(0, Math.floor((frame - start) / 0.7));
  const visible = line.slice(0, Math.min(chars, line.length));
  const done = chars >= line.length;
  return (
    <div
      style={{
        fontFamily: FONTS.mono,
        fontSize: 34,
        color: done ? COLORS.text : COLORS.accent,
        minHeight: 52,
        whiteSpace: 'pre',
      }}
    >
      {visible}
      {!done && frame >= start && (
        <span style={{color: COLORS.accent}}>▌</span>
      )}
    </div>
  );
};

export const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const titleOp = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});
  const titleY = interpolate(frame, [0, 20], [30, 0], {extrapolateRight: 'clamp'});
  const subOp = interpolate(frame, [20, 40], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: FONTS.sans,
      }}
    >
      <div
        style={{
          opacity: titleOp,
          transform: `translateY(${titleY}px)`,
          fontSize: 84,
          fontWeight: 700,
          color: COLORS.text,
        }}
      >
        BAMOE <span style={{color: COLORS.accent}}>v8 → v9.5</span> Project
        Migrator
      </div>
      <div
        style={{
          opacity: subOp,
          marginTop: 24,
          fontSize: 32,
          color: COLORS.dim,
          maxWidth: 1300,
          textAlign: 'center',
        }}
      >
        Turns your old IBM BAMOE v8 project into a new BAMOE v9.5 project,
        automatically, using Devin.
      </div>
      {frame >= 90 && (
        <div
          style={{
            marginTop: 70,
            backgroundColor: COLORS.panel,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 12,
            padding: '36px 48px',
            opacity: interpolate(frame, [90, 95], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }),
          }}
        >
          {STEPS.map((line, i) => (
            <TypedLine key={i} line={line} start={90 + i * 10} />
          ))}
        </div>
      )}
    </AbsoluteFill>
  );
};
