import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONTS} from '../style';

const LINES: {path: string; note: string}[] = [
  {path: 'v9-projects/', note: ''},
  {path: '└── my-project/', note: ''},
  {path: '    ├── pom.xml', note: 'new; Quarkus + Kogito'},
  {path: '    ├── migration-inventory.md', note: 'everything Devin found in your v8 project'},
  {path: '    ├── migration-status.md', note: 'the 10 steps, ticked off as they finish'},
  {path: '    └── src/main/', note: ''},
  {path: '        ├── java/…', note: 'updated Java (jakarta.*, new handlers)'},
  {path: '        └── resources/', note: ''},
  {path: '            ├── application.properties', note: 'replaces all the META-INF xml files'},
  {path: '            ├── *.bpmn', note: 'upgraded diagrams, Java scripts'},
  {path: '            └── custom-forms-dev/*.tsx', note: 'regenerated forms (if you had .frm files)'},
];

export const OutputTree: React.FC = () => {
  const frame = useCurrentFrame();

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
        What comes out
      </div>
      <div
        style={{
          backgroundColor: COLORS.panel,
          border: `1px solid ${COLORS.border}`,
          borderRadius: 12,
          padding: '32px 48px',
          fontFamily: FONTS.mono,
          fontSize: 25,
          lineHeight: 1.7,
        }}
      >
        {LINES.map((l, i) => {
          const start = 20 + i * 30;
          const pathOp = interpolate(frame, [start, start + 10], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const noteOp = interpolate(
            frame,
            [start + 10, start + 22],
            [0, 1],
            {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
          );
          return (
            <div key={i} style={{opacity: pathOp, color: COLORS.text, whiteSpace: 'pre'}}>
              {l.path}
              {l.note && (
                <span style={{opacity: noteOp, color: COLORS.dim}}>
                  {'  '}← {l.note}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
