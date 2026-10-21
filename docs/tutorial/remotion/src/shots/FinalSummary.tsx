import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONTS} from '../style';

type Line = {text: string; mono?: boolean; bold?: boolean; gap?: number};

const LINES: Line[] = [
  {text: 'Done — I migrated your project.', bold: true},
  {text: 'Found in the v8 export:', bold: true, gap: 26},
  {text: '• 1 BPMN process, 1 custom work item definition, kmodule.xml'},
  {text: 'Created:', bold: true, gap: 26},
  {text: 'v9-projects/v8-app/', mono: true},
  {text: '• new pom.xml (BAMOE 9.5, Quarkus, Java 21)'},
  {text: '• application.properties replacing kmodule.xml'},
  {text: '• upgraded BPMN + regenerated forms'},
  {text: 'Still needs a person:', bold: true, gap: 26},
  {text: '• Review the regenerated forms in Developer Tools'},
  {text: '• Set quarkus.oidc.* for login'},
  {text: '• Provision a new PostgreSQL database (v8 DB can\'t be reused)'},
];

const REVEAL_EVERY = 30;
const REVEAL_START = 30;

export const FinalSummary: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: FONTS.sans,
        paddingBottom: 120,
      }}
    >
      <div
        style={{
          width: 1200,
          backgroundColor: COLORS.panel,
          border: `1px solid ${COLORS.border}`,
          borderRadius: 16,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div
          style={{
            padding: '18px 28px',
            borderBottom: `1px solid ${COLORS.border}`,
            color: COLORS.dim,
            fontSize: 26,
          }}
        >
          Devin — session
        </div>
        <div style={{padding: '36px 44px'}}>
          <div
            style={{
              fontSize: 30,
              lineHeight: 1.55,
              backgroundColor: COLORS.bg,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 16,
              borderTopLeftRadius: 4,
              padding: '30px 36px',
            }}
          >
            {LINES.map((l, i) => {
              const at = REVEAL_START + i * REVEAL_EVERY;
              const op = interpolate(frame, [at, at + 14], [0, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              });
              const y = interpolate(frame, [at, at + 14], [12, 0], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              });
              return (
                <div
                  key={i}
                  style={{
                    opacity: op,
                    transform: `translateY(${y}px)`,
                    marginTop: l.gap ?? 0,
                    fontWeight: l.bold ? 700 : 400,
                    fontFamily: l.mono ? FONTS.mono : FONTS.sans,
                    color: l.mono ? COLORS.accent : l.bold ? COLORS.text : COLORS.dim,
                  }}
                >
                  {l.text}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
