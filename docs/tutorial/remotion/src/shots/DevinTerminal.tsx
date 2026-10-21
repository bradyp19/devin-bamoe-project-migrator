import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONTS} from '../style';

type Line = {text: string; at: number; color?: string};

const LINES: Line[] = [
  {text: '$ unzip v8-app.zip -d v8-projects/', at: 10, color: COLORS.text},
  {text: '  inflating: v8-projects/v8-app/pom.xml', at: 40, color: COLORS.dim},
  {text: '  inflating: v8-projects/v8-app/src/main/resources/evaluation.bpmn', at: 55, color: COLORS.dim},
  {text: '  inflating: v8-projects/v8-app/src/main/resources/META-INF/kmodule.xml', at: 70, color: COLORS.dim},
  {text: '  inflating: v8-projects/v8-app/global/WorkDefinitions.wid', at: 85, color: COLORS.dim},
  {text: '  … 42 files extracted', at: 100, color: COLORS.dim},
  {text: '$ ls v8-projects/', at: 150, color: COLORS.text},
  {text: 'v8-app', at: 170, color: COLORS.dim},
  {text: '$ find v8-projects -name pom.xml', at: 220, color: COLORS.text},
  {text: 'v8-projects/v8-app/pom.xml', at: 240, color: COLORS.dim},
  {text: '✓ Found Maven project — auditing v8 assets', at: 290, color: COLORS.green},
  {text: '  • 1 BPMN process', at: 330, color: COLORS.dim},
  {text: '  • 1 .wid work item definition', at: 360, color: COLORS.dim},
  {text: '  • kmodule.xml (will be replaced)', at: 390, color: COLORS.dim},
  {text: 'Creating migration-inventory.md …', at: 440, color: COLORS.dim},
  {text: 'Creating migration-status.md …', at: 480, color: COLORS.dim},
];

const LINE_H = 56;
const VISIBLE = 11;

export const DevinTerminal: React.FC = () => {
  const frame = useCurrentFrame();

  const shown = LINES.filter((l) => frame >= l.at);
  const overflow = Math.max(0, shown.length - VISIBLE);
  const scroll = interpolate(frame, [0, 600], [0, overflow * LINE_H], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: FONTS.sans,
        paddingBottom: 110,
      }}
    >
      <div style={{fontSize: 44, color: COLORS.text, marginBottom: 40}}>
        Devin unpacks the project
      </div>
      <div
        style={{
          width: 1500,
          height: VISIBLE * LINE_H + 90,
          backgroundColor: COLORS.panel,
          border: `1px solid ${COLORS.border}`,
          borderRadius: 12,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* title bar */}
        <div
          style={{
            height: 54,
            borderBottom: `1px solid ${COLORS.border}`,
            display: 'flex',
            alignItems: 'center',
            paddingLeft: 20,
            gap: 10,
          }}
        >
          {[COLORS.red, COLORS.dim, COLORS.green].map((c, i) => (
            <div
              key={i}
              style={{width: 16, height: 16, borderRadius: 8, backgroundColor: c}}
            />
          ))}
          <span style={{marginLeft: 16, color: COLORS.dim, fontSize: 24}}>
            Devin — terminal
          </span>
        </div>
        {/* body */}
        <div style={{flex: 1, overflow: 'hidden', position: 'relative'}}>
          <div
            style={{
              position: 'absolute',
              top: 24 - scroll,
              left: 0,
              right: 0,
              padding: '0 32px',
              fontFamily: FONTS.mono,
              fontSize: 30,
              lineHeight: `${LINE_H}px`,
              whiteSpace: 'nowrap',
            }}
          >
            {shown.map((l, i) => (
              <div key={i} style={{color: l.color}}>
                {l.text}
              </div>
            ))}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
