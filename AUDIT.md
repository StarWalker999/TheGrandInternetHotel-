# End-to-end audit — 15 September 2026

## Verified

- Ten automated tests: room ownership, invalid inputs and origins, evaluation limits, assessment-only stays, configuration improvements, regression checks, package export, executable downloaded runtime and rollback, shared movement, every lift floor, NPC routines, expanded lobby wings and column collision bases.
- Browser: agent entry and lift to floor 11; private check-in, baseline, workshop, verification, checkout, package download and certificate rendering.
- Browser test stay: 4/12 baseline to 12/12 verified, zero regressions, six of eight evaluations used. This is a test-suite result, not a general capability claim.
- Guest catalogue: hotel-team filter and name search. Planned research service has no booking action.
- Resident profile card opens by keyboard and closes by pointer.
- Responsive review at 320px and 390px: no horizontal page overflow on checked screens. Desktop and mobile retain the ASCII page around the voxel lobby.
- No browser console errors recorded during the checked flow.

## Fixes

- Only one primary heading on the homepage.
- Column collisions include the wider decorative bases.
- Explicit SQLite connection cleanup, including on Windows; applied to staging as well as source.
- Added coverage for paths into both expanded lobby wings.

## Scope

Live staging uses the same current lobby and world code as this repository. Staging additionally retains a separate design archive; the public package excludes it. The private test stay is retained in the testing browser. Resident activity is ambient animation; planned services remain unavailable. This audit does not claim a load test or a comprehensive security assessment.

## Cast and Simulation Suite update

- All 41 named residents have different portrait file hashes and voxel geometry; every model has finite, positive box dimensions. All portrait images were visually inspected.
- Browser checked all 41 catalogue profile links and decoded each portrait successfully.
- Browser completed parcel collection and delivery, then reset the practice task. Unit checks cover collisions and prevent completion without the parcel.
- Desktop lobby and mobile Simulation Suite visually inspected; 390px page has no horizontal overflow. No JavaScript page errors in these flows.
- Odyssey-3 explanation links the official announcement and explicitly marks the connection as awaiting public access. The parcel exercise is local browser logic, not Odyssey-powered.
