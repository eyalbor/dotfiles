export interface MethodologyMode {
  name: 'advance' | 'light';
  description: string;
  targetTokens: string;
  systemInstruction: string;
}
