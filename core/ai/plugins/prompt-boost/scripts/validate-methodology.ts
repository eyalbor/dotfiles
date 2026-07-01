#!/usr/bin/env tsx
import { ADVANCE_MODE, LIGHT_MODE, validateAllMethodologies } from '../src/methodology/index.js';

function printValidationResults(
  mode: string,
  errors: string[],
  instruction: string
) {
  console.log(`\n📋 Validating ${mode} Mode...`);
  console.log(`   Length: ${instruction.length} characters`);

  if (errors.length === 0) {
    console.log(`   ✅ ${mode} mode validation passed!`);
  } else {
    console.log(`   ❌ ${mode} mode validation failed:`);
    errors.forEach((err) => console.log(`      - ${err}`));
  }
}

function main() {
  console.log('🔍 Validating Prompt Enhancement Methodologies\n');
  console.log('━'.repeat(60));

  const result = validateAllMethodologies(
    ADVANCE_MODE.systemInstruction,
    LIGHT_MODE.systemInstruction
  );

  printValidationResults(
    'Advance',
    result.advanceErrors,
    ADVANCE_MODE.systemInstruction
  );
  printValidationResults(
    'Light',
    result.lightErrors,
    LIGHT_MODE.systemInstruction
  );

  console.log('\n' + '━'.repeat(60));

  if (result.isValid) {
    console.log('\n✨ All methodologies are valid!\n');
    console.log('📊 Summary:');
    console.log(`   - Advance Mode: ${ADVANCE_MODE.targetTokens}`);
    console.log(`   - Light Mode: ${LIGHT_MODE.targetTokens}`);
    console.log('\n✅ Ready to generate documentation');
    process.exit(0);
  } else {
    console.log('\n❌ Validation failed. Please fix the errors above.\n');
    console.log('💡 Tips:');
    console.log('   - Check that all mandatory sections are present');
    console.log('   - Ensure hallucination prevention instructions are included');
    console.log('   - Verify output-only directive is present');
    console.log('   - Confirm FINAL REMINDER is at the end');
    process.exit(1);
  }
}

main();
