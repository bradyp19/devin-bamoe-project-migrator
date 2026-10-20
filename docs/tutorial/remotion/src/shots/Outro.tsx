import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONTS} from '../style';

const PITFALLS = [
  'I uploaded a .zip',
  '"I can\'t find pom.xml"',
  'Folder name has spaces ("my app copy")',
  'Only a .bpmn file, no pom.xml',
  'Two folders in v8-projects/',
  '"Build: not-run"',
  'Forms look missing',
  'Devin asks a question and waits',
];

export const Outro: React.FC = () => {
  const frame = useCurrentFrame();

  // Scroll the pitfall list upward through the first ~200 frames.
  const scrollY = interpolate(frame, [0, 200], [80, -140], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const listOp = interpolate(frame, [220, 250], [1, 0.15], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const cardOp = interpolate(frame, [230, 260], [0, 1], {
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
          fontSize: 40,
          color: COLORS.text,
          height: 90,
          display: 'flex',
          alignItems: 'center',
        }}
      >
        If something looks odd…
      </div>
      <div style={{height: 340, overflow: 'hidden', opacity: listOp}}>
        <div style={{transform: `translateY(${scrollY}px)`}}>
          {PITFALLS.map((p, i) => (
            <div
              key={i}
              style={{
                fontSize: 30,
                color: COLORS.dim,
                padding: '10px 40px',
                borderBottom: `1px solid ${COLORS.border}`,
                minWidth: 900,
              }}
            >
              {p}
            </div>
          ))}
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          top: '58%',
          opacity: cardOp,
          backgroundColor: COLORS.panel,
          border: `2px solid ${COLORS.accent}`,
          borderRadius: 14,
          padding: '32px 60px',
          fontSize: 44,
          fontWeight: 700,
          color: COLORS.text,
        }}
      >
        README → <span style={{color: COLORS.accent}}>Common pitfalls</span>
      </div>
    </AbsoluteFill>
  );
};
