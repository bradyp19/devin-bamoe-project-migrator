import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONTS} from '../style';

export const NestedZipFix: React.FC = () => {
  const frame = useCurrentFrame();

  // Phase 1 (0-90): show the nested tree.
  // Phase 2 (90-240): red marker highlights the inner my-app/.
  // Phase 3 (240-330): the inner folder slides up one level.
  // Phase 4 (330+): marker turns green, success message appears.
  const t = interpolate(frame, [240, 330], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const folderIndent = (2 - t) * 4; // 8ch -> 4ch
  const childIndent = (3 - t) * 4; // 12ch -> 8ch
  const isFixed = frame >= 330;
  const markerColor = isFixed ? COLORS.green : COLORS.red;
  const markerOn = frame >= 90;
  const msgOp = interpolate(frame, [350, 380], [0, 1], {
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
      <div style={{fontSize: 44, color: COLORS.text, marginBottom: 40}}>
        Gotcha: a folder inside a folder
      </div>
      <div
        style={{
          backgroundColor: COLORS.panel,
          border: `1px solid ${COLORS.border}`,
          borderRadius: 12,
          padding: '36px 48px',
          fontFamily: FONTS.mono,
          fontSize: 32,
          lineHeight: 1.9,
          minWidth: 900,
        }}
      >
        <div style={{color: COLORS.text}}>v8-projects/</div>
        <div style={{color: COLORS.text, paddingLeft: '4ch'}}>my-app/</div>
        <div
          style={{
            paddingLeft: `${folderIndent}ch`,
          }}
        >
          <span
            style={{
              display: 'inline-block',
              border: markerOn
                ? `3px solid ${markerColor}`
                : '3px solid transparent',
              borderRadius: 8,
              padding: '0 14px',
              color: COLORS.text,
            }}
          >
            my-app/
          </span>
        </div>
        <div style={{paddingLeft: `${childIndent}ch`, color: COLORS.accent}}>
          pom.xml
        </div>
        <div style={{paddingLeft: `${childIndent}ch`, color: COLORS.text}}>
          src/
        </div>
      </div>
      <div
        style={{
          marginTop: 50,
          opacity: msgOp,
          fontSize: 40,
          color: COLORS.green,
          fontWeight: 700,
        }}
      >
        ✓ Devin moved it up one level
      </div>
    </AbsoluteFill>
  );
};
