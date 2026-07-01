export * from './types';
export * from './advance';
export * from './light';
export * from './validator';

export const METHODOLOGIES = {
  advance: ADVANCE_MODE,
  light: LIGHT_MODE,
} as const;

export type MethodologyName = keyof typeof METHODOLOGIES;

// Re-export for convenience
import { ADVANCE_MODE } from './advance';
import { LIGHT_MODE } from './light';
