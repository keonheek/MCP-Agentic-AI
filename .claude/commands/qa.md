Review, audit, and fix a business output until all quality scores >= 9.0.

Read `tools/qa-registry.json` to find the generator and regenerate command for the given output type.

Then invoke the qa-agent with:
- output_path: the path to the output file or folder to review
- generator_path: from the registry
- regenerate_command: from the registry
- target_spec: from the registry

If the output type is not in the registry, ask the user for the generator_path and regenerate_command before proceeding.

Usage:
  /qa [output_path] [output_type]

Examples:
  /qa projects/geo-agency/team_test_output/geo_audit_세무법인_엑스퍼트_2026-03-25.pdf geo-audit-pdf
  /qa projects/sme-diagnostic-ai/output/consulting_deck.pptx sme-deck
  /qa projects/geo-agency/deliverables/세무법인_엑스퍼트_2026-03-25/ geo-kit

If no arguments: ask the user which output to QA and look up the type from the registry.

ARGUMENTS: $ARGUMENTS
