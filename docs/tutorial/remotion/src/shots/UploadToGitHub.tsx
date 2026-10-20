import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONTS} from '../style';

export const UploadToGitHub: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Zip card drags from left into the drop zone between frames 50 and 150.
  const zipX = interpolate(frame, [50, 150], [0, 620], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const zipScale = interpolate(frame, [150, 180], [1, 0.2], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const zipOp = interpolate(frame, [150, 190], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // "Commit changes" button appears and pulses.
  const btnIn = spring({frame: frame - 210, fps, config: {damping: 12}});
  const pulse = 1 + 0.06 * Math.sin(frame / 6);
  const btnOp = interpolate(frame, [205, 220], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const checkOp = interpolate(frame, [190, 210], [0, 1], {
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
      <div style={{fontSize: 44, color: COLORS.text, marginBottom: 60}}>
        Upload to <span style={{fontFamily: FONTS.mono}}>v8-projects/</span>
      </div>
      <div style={{display: 'flex', alignItems: 'center', gap: 80}}>
        {/* Zip card being dragged */}
        <div
          style={{
            transform: `translateX(${zipX}px) scale(${zipScale})`,
            opacity: zipOp,
            width: 280,
            height: 180,
            backgroundColor: COLORS.panel,
            border: `2px solid ${COLORS.accent}`,
            borderRadius: 12,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            gap: 12,
          }}
        >
          <div style={{fontSize: 64}}>🗜️</div>
          <div style={{fontFamily: FONTS.mono, fontSize: 26, color: COLORS.text}}>
            my-project.zip
          </div>
        </div>
        {/* Drop zone */}
        <div
          style={{
            width: 560,
            height: 340,
            border: `3px dashed ${COLORS.accent}`,
            borderRadius: 16,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            gap: 16,
            backgroundColor: COLORS.panel,
          }}
        >
          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 40,
              color: COLORS.accent,
              fontWeight: 700,
            }}
          >
            v8-projects/
          </div>
          <div style={{fontSize: 26, color: COLORS.dim}}>
            Drag files here to add them
          </div>
          <div
            style={{
              opacity: checkOp,
              fontSize: 30,
              color: COLORS.green,
              fontWeight: 600,
            }}
          >
            ✓ my-project.zip added
          </div>
        </div>
      </div>
      <div
        style={{
          marginTop: 70,
          opacity: btnOp,
          transform: `scale(${btnIn * pulse})`,
          backgroundColor: COLORS.green,
          color: '#000',
          fontSize: 34,
          fontWeight: 700,
          padding: '18px 48px',
          borderRadius: 10,
        }}
      >
        Commit changes
      </div>
    </AbsoluteFill>
  );
};
