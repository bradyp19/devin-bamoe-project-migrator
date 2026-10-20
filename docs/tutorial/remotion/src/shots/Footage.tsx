import React from 'react';
import {AbsoluteFill, getStaticFiles, OffthreadVideo, staticFile} from 'remotion';
import {COLORS, FONTS} from '../style';
import type {Shot} from '../script';

export const Footage: React.FC<{shot: Shot}> = ({shot}) => {
  // getStaticFiles() is evaluated at render time, so a missing raw file
  // renders the placeholder instead of crashing.
  const files = getStaticFiles();
  const exists = shot.rawFile
    ? files.some((f) => f.name === shot.rawFile)
    : false;

  if (!exists) {
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
            border: `3px dashed ${COLORS.border}`,
            borderRadius: 16,
            padding: '60px 80px',
            textAlign: 'center',
            maxWidth: 1400,
          }}
        >
          <div style={{fontSize: 56, color: COLORS.dim, fontWeight: 700}}>
            Recording pending — shot {shot.id}
          </div>
          <div
            style={{
              marginTop: 40,
              fontSize: 30,
              color: COLORS.text,
            }}
          >
            <span style={{color: COLORS.accent}}>Screen:</span> {shot.screen}
          </div>
          <div style={{marginTop: 16, fontSize: 30, color: COLORS.text}}>
            <span style={{color: COLORS.accent}}>Action:</span> {shot.action}
          </div>
          <div
            style={{
              marginTop: 40,
              fontFamily: FONTS.mono,
              fontSize: 24,
              color: COLORS.dim,
            }}
          >
            save as public/{shot.rawFile}
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg}}>
      <OffthreadVideo
        src={staticFile(shot.rawFile!)}
        style={{width: '100%', height: '100%', objectFit: 'contain'}}
      />
    </AbsoluteFill>
  );
};
