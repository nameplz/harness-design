# Stop Conditions

The harness must stop automatically when any of the following applies.

## Immediate Stop

- A critical security issue is discovered.
- A destructive migration or data-loss risk is detected.
- Requirements are contradictory enough that implementation would be wasteful.
- The environment is missing required credentials or infrastructure and no safe fallback exists.

## Budget Or Time Stop

- Hard budget has been reached.
- Maximum allowed run time has been reached.
- Maximum loop count has been reached.

## Repetition Stop

- The same failure pattern has repeated the configured number of times.
- QA findings are not converging.
- The generator keeps solving symptoms without fixing root causes.

## On Stop

When stopping, the harness must write:

- the current state
- the blocking reason
- what was completed
- what remains
- the recommended next human decision
