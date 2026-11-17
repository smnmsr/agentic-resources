# Reviewer prompt attribution

`reviewer.md` adapts the investigation/evidence gates from OpenLens's
`agents/bugs.md` and `agents/security.md`, pinned at commit
[a3f984dfc03b620934e8b188e6d9fa8286a42287](https://github.com/Traves-Theberge/openlens/tree/a3f984dfc03b620934e8b188e6d9fa8286a42287/agents)
(October 24, 2026). OpenLens's MIT copyright notice is `Copyright (c) 2026`
with no named holder. Its framework, language checklists and JSON report format
are not imported. Some upstream examples overstate security guarantees; only
the evidence-driven workflow is adapted, not those examples.

It also adapts the review priorities, connected-code inspection and smallest-fix
criteria from `@dietrichgebert/ponytail`'s `ponytail-review` skill, installed
package version `5.3.3`, inspected November 17, 2026.
Source: https://github.com/dietrichgebert/ponytail .

Both sources are MIT licensed. Their notices and the common MIT terms are
included in the reviewer prompt so the single-file published config carries them.
