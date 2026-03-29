'use client';

import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { format, parseISO } from 'date-fns';

interface HealthTrendProps {
  checkins: Array<{
    checked_in_at: string;
    mood: number;
  }>;
}

export function HealthTrend({ checkins }: HealthTrendProps) {
  if (checkins.length < 2) return null;

  const data = [...checkins]
    .reverse()
    .map((c) => ({
      date: format(parseISO(c.checked_in_at), 'MMM d'),
      mood: c.mood,
    }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="arcane-glass p-4"
    >
      <p className="label-section mb-3">MOOD TREND</p>
      <div className="h-[120px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis
              dataKey="date"
              tick={{ fontSize: 9, fill: 'var(--color-text-secondary)', fontFamily: 'monospace' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              domain={[1, 5]}
              ticks={[1, 3, 5]}
              tick={{ fontSize: 9, fill: 'var(--color-text-secondary)', fontFamily: 'monospace' }}
              axisLine={false}
              tickLine={false}
              width={20}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--color-surface-0)',
                border: '1px solid var(--color-neon-cyan / 0.15)',
                borderRadius: '8px',
                fontFamily: 'monospace',
                fontSize: '11px',
              }}
              labelStyle={{ color: 'var(--color-text-secondary)' }}
              itemStyle={{ color: 'var(--color-neon-cyan)' }}
            />
            <Line
              type="monotone"
              dataKey="mood"
              stroke="var(--color-neon-cyan)"
              strokeWidth={2}
              dot={{ r: 3, fill: 'var(--color-neon-cyan)' }}
              activeDot={{ r: 5, fill: 'var(--color-neon-cyan)' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
