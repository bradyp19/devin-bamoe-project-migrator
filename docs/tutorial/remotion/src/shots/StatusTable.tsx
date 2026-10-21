import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONTS} from '../style';

type Row = {name: string; result: 'done' | 'skipped'; reason?: string};

const ROWS: Row[] = [
  {name: 'Sub-Task 1 — Audit the v8 Project and Classify Assets', result: 'done'},
  {name: 'Sub-Task 2 — Migrate Project Structure and POM', result: 'done'},
  {name: 'Sub-Task 3 — Migrate BPMN Workflow Assets', result: 'done'},
  {name: 'Sub-Task 4 — Migrate DMN Decision Assets', result: 'skipped', reason: 'no DMN assets'},
  {name: 'Sub-Task 5 — Migrate DRL Rules, Decision Tables, and Test Scenarios', result: 'skipped', reason: 'no DRL assets'},
  {name: 'Sub-Task 6 — Migrate Custom WorkItemHandlers', result: 'done'},
  {name: 'Sub-Task 7 — Migrate Security, Auth, UserGroupCallback, and AssignmentStrategy', result: 'done'},
  {name: 'Sub-Task 8 — Migrate Forms', result: 'done'},
  {name: 'Sub-Task 9 — Migrate Event Streaming and Event Listeners', result: 'skipped', reason: 'none present'},
  {name: 'Sub-Task 10 — Runtime Deployment and Live-Data Strategy', result: 'done'},
];

const FLIP_START = 60;
const FLIP_EVERY = 48;

export const StatusTable: React.FC = () => {
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
      <div style={{fontSize: 40, color: COLORS.text, marginBottom: 28}}>
        <span style={{fontFamily: FONTS.mono, color: COLORS.accent}}>
          v9-projects/v8-app/migration-status.md
        </span>
      </div>
      <div
        style={{
          width: 1560,
          backgroundColor: COLORS.panel,
          border: `1px solid ${COLORS.border}`,
          borderRadius: 12,
          overflow: 'hidden',
          fontFamily: FONTS.mono,
          fontSize: 26,
        }}
      >
        {ROWS.map((row, i) => {
          const flipAt = FLIP_START + i * FLIP_EVERY;
          const flipped = frame >= flipAt;
          const flash = interpolate(frame, [flipAt, flipAt + 14], [1, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const status = flipped ? `[x] ${row.result}` : '[ ] pending';
          const statusColor = !flipped
            ? COLORS.dim
            : row.result === 'done'
              ? COLORS.green
              : COLORS.dim;
          return (
            <div
              key={i}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '13px 28px',
                borderBottom: `1px solid ${COLORS.border}`,
                backgroundColor: `rgba(66, 190, 101, ${0.12 * flash})`,
              }}
            >
              <span style={{color: COLORS.text}}>{row.name}</span>
              <span style={{color: statusColor, marginLeft: 32, whiteSpace: 'nowrap'}}>
                {status}
                {flipped && row.reason ? ` (${row.reason})` : ''}
              </span>
            </div>
          );
        })}
        <div
          style={{
            padding: '13px 28px',
            color: COLORS.dim,
          }}
        >
          **Build:** not-run
        </div>
      </div>
    </AbsoluteFill>
  );
};
