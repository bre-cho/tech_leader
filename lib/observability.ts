export const observability = {
  recordFallbackActivation: (_scope: string, _mode: string) => void 0,
  recordMetric: (_name: string, _value: number, _tags?: Record<string, unknown>) => void 0,
  recordEvent: (_name: string, _payload?: Record<string, unknown>) => void 0,
};
