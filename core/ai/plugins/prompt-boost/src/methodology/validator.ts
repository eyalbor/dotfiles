/**
 * Validates that a methodology system instruction meets quality standards
 */
export function validateMethodology(systemInstruction: string): {
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  // Check minimum length
  if (systemInstruction.length < 500) {
    errors.push('System instruction is too short (minimum 500 characters)');
  }

  // Check for mandatory sections in Advance mode
  const advanceRequiredSections = [
    'Role & Task Assignment',
    'Context Section',
    'Detailed Instructions',
    'Constraints & Boundaries',
    'Output Format Specification',
    'Examples',
    'Hallucination Prevention',
    'CRITICAL REPETITION',
    'META-INSTRUCTIONS',
  ];

  // Check for mandatory sections in Light mode
  const lightRequiredSections = [
    'ROLE & TASK ASSIGNMENT',
    'CONTEXT SECTION',
    'DETAILED INSTRUCTIONS',
    'EXAMPLE',
    'HALLUCINATION PREVENTION',
    'CRITICAL REPETITION',
    'META-INSTRUCTIONS',
  ];

  // Determine which mode based on content
  const isAdvanceMode = systemInstruction.includes('STRUCTURAL FOUNDATION');
  const isLightMode = systemInstruction.includes('Light methodology');

  if (isAdvanceMode) {
    for (const section of advanceRequiredSections) {
      if (!systemInstruction.includes(section)) {
        errors.push(`Missing required Advance mode section: ${section}`);
      }
    }
  } else if (isLightMode) {
    for (const section of lightRequiredSections) {
      if (!systemInstruction.includes(section)) {
        errors.push(`Missing required Light mode section: ${section}`);
      }
    }
  } else {
    errors.push('Cannot determine methodology mode (Advance or Light)');
  }

  // Check for hallucination prevention instructions
  const hallucinationKeywords = [
    "don't know",
    'uncertain',
    'step-by-step',
    'confidence',
  ];

  let hasHallucinationPrevention = false;
  for (const keyword of hallucinationKeywords) {
    if (systemInstruction.toLowerCase().includes(keyword)) {
      hasHallucinationPrevention = true;
      break;
    }
  }

  if (!hasHallucinationPrevention) {
    errors.push(
      'Missing hallucination prevention instructions (uncertainty handling, step-by-step thinking, etc.)'
    );
  }

  // Check for output-only directive
  if (!systemInstruction.includes('Return ONLY') && !systemInstruction.includes('return ONLY')) {
    errors.push('Missing output-only directive');
  }

  // Check for FINAL REMINDER
  if (!systemInstruction.includes('FINAL REMINDER')) {
    errors.push('Missing FINAL REMINDER at end');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validates both advance and light methodologies
 */
export function validateAllMethodologies(
  advanceInstruction: string,
  lightInstruction: string
): {
  isValid: boolean;
  advanceErrors: string[];
  lightErrors: string[];
} {
  const advanceResult = validateMethodology(advanceInstruction);
  const lightResult = validateMethodology(lightInstruction);

  return {
    isValid: advanceResult.isValid && lightResult.isValid,
    advanceErrors: advanceResult.errors,
    lightErrors: lightResult.errors,
  };
}
