import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONTS} from '../style';

const PROMPT = 'Migrate my project';
const TYPE_START = 20;
const CHARS_PER_4F = 1; // one char every ~4 frames
const SEND_AT = 150;
const BUBBLE_AT = 170;

export const TypePrompt: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const typed = Math.min(
    PROMPT.length,
    Math.max(0, Math.floor((frame - TYPE_START) / 4) * CHARS_PER_4F)
  );
  const doneTyping = typed >= PROMPT.length;
  const sent = frame >= BUBBLE_AT;
  const cursorOn = Math.floor(frame / 15) % 2 === 0 && !doneTyping;

  const sendGlow = interpolate(frame, [SEND_AT, SEND_AT + 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const bubbleIn = spring({frame: frame - BUBBLE_AT, fps, config: {damping: 14}});
  const workingOp = interpolate(frame, [200, 220], [0, 1], {
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
      <div
        style={{
          width: 1100,
          height: 780,
          backgroundColor: COLORS.panel,
          border: `1px solid ${COLORS.border}`,
          borderRadius: 16,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* header */}
        <div
          style={{
            padding: '18px 28px',
            borderBottom: `1px solid ${COLORS.border}`,
            color: COLORS.dim,
            fontSize: 26,
            display: 'flex',
            justifyContent: 'space-between',
          }}
        >
          <span>Devin — new session</span>
          <span>devin-bamoe-project-migrator</span>
        </div>

        {/* chat area */}
        <div style={{flex: 1, padding: '36px 40px', position: 'relative'}}>
          {sent && (
            <div
              style={{
                transform: `scale(${bubbleIn})`,
                transformOrigin: 'bottom right',
                alignSelf: 'flex-end',
                marginLeft: 'auto',
                width: 'fit-content',
                maxWidth: '80%',
                backgroundColor: COLORS.accent,
                color: COLORS.text,
                fontSize: 38,
                fontWeight: 600,
                padding: '24px 36px',
                borderRadius: 20,
                float: 'right',
                clear: 'both',
              }}
            >
              {PROMPT}
            </div>
          )}
          <div
            style={{
              position: 'absolute',
              bottom: 36,
              left: 40,
              opacity: workingOp,
              color: COLORS.dim,
              fontSize: 30,
            }}
          >
            Devin is working…
          </div>
        </div>

        {/* input bar */}
        <div
          style={{
            margin: '0 28px 28px',
            border: `1px solid ${COLORS.border}`,
            borderRadius: 12,
            padding: '26px 30px',
            fontSize: 38,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: COLORS.bg,
          }}
        >
          <span style={{fontFamily: FONTS.mono, color: sent ? COLORS.dim : COLORS.text}}>
            {sent ? 'Ask Devin anything…' : PROMPT.slice(0, typed)}
            {!sent && (
              <span
                style={{
                  display: 'inline-block',
                  width: 22,
                  height: 44,
                  verticalAlign: 'middle',
                  marginLeft: 4,
                  backgroundColor: cursorOn ? COLORS.text : 'transparent',
                }}
              />
            )}
          </span>
          {!sent && (
            <span
              style={{
                fontSize: 28,
                fontWeight: 700,
                color: sendGlow > 0 ? COLORS.text : COLORS.dim,
                backgroundColor: `rgba(15, 98, 254, ${0.25 + 0.75 * sendGlow})`,
                borderRadius: 8,
                padding: '10px 24px',
                boxShadow: `0 0 ${30 * sendGlow}px rgba(15, 98, 254, ${0.8 * sendGlow})`,
              }}
            >
              Send ↑
            </span>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
