# Bubble Man data-sharing outline

**DRAFT for discussion - 11 October 2026. Not sent or agreed.**

**My inference - proposed terms throughout:** this is an outline for the utility's authorised data owner and legal/privacy reviewers to turn into an agreement. Party names, dates and selected terms remain open. It grants no present data access and is not a document to sign as it stands.

**Unverified:** the receiving party's legal identity, a suitable zone, the utility's authority to share each file, personal-data content, applicable approvals and actual storage/providers. Do not assume “Bubble Man” is a registered contracting entity.

## 1. Parties and responsible people

Record `[utility's full legal name and authorised representative]` and `[recipient's full legal name/identifier and representative]`. Name the operational lead, data custodian, privacy/security lead and incident contacts. Specify any legally applicable controller/processor roles; do not assign them solely from a project title.

## 2. Purpose and permitted stages

Limit the purpose to checking whether the existing night-flow warning method is useful in **one agreed water zone**, using a written evaluation protocol.

1. **Compatibility stage:** a 2-4 week readings-only sample and zone/meter description, to check meanings, quality and file compatibility. This is not a detection-performance test.
2. **Historical trial, separately authorised:** agreed dates covering at least a year, operating logs and independently understood incident records. Fix the rule, reading-quality exclusions, scoring and workload criteria before incident outcomes are opened. Keep incident files with the utility's custodian until warnings and their audit record are locked.
3. **Live shadow trial, separately agreed later:** define staff, inspections, control visits, data arrival and workload. Historical analysis gives no automatic permission for live access or field operations.

No unrelated use, onward sale, customer profiling, public release, unrelated model training or product deployment. Any changed purpose, recipient, tool/provider or experiment needs written agreement first. Baseline calculation specifically approved by the evaluation protocol is part of the trial purpose.

## 3. Data schedule and minimisation

Attach an agreed inventory with file/schema, zone, dates, cadence, units, timestamp convention, quality flags, custodian and sensitivity for each category:

| Stage / category | Proposed scope |
|---|---|
| Initial readings | Boundary-meter IDs, times, values, units and flags; no incident rows in the first sample. |
| Zone and meters | Inlets/outlets/transfers, valve-boundary status, supply regime, storage and meter/value semantics. Internal tank levels/geometry only if required and authorised. |
| Operating logs | Timed supply, pump/valve/pressure changes and meter faults relevant to the chosen zone. |
| Incident/inspection records | Stable opaque incident IDs, first report, confirmation and repair times kept separate; approved zone/asset location, discovery method and completed/incomplete/negative inspections. |
| Outputs and audit | Canonical files, source mappings/audits, warning lists, plots, reports, hashes and relevant processing logs. Apply the same confidentiality classification where these reveal source information. |

Avoid customer names, phone numbers, account details and unrestricted free text. The utility can retain the identity lookup and provide opaque IDs. Do not silently round dates or coordinates: agree a privacy-preserving representation, and record resulting evaluation limits. Replacing names with IDs does not by itself establish anonymity.

## 4. Authority and personal-data review

Confirm rights to provide data held by the utility, contractors and meter-platform vendors. Record the approved access scope and any export conditions. Identify any personal data and the applicable lawful basis, notices, roles and authorisations before transfer. Where personal data are unnecessary, remove them through a documented utility-approved process.

**Verified (official source):** Rwanda's law includes information about directly or indirectly identifiable people, including location identifiers, in its personal-data definition. [DPO, Article 3](https://dpo.gov.rw/dpp-law/general-provisions).

**Verified (official source):** Articles 48-50 address cross-border transfer, contracts and personal-data storage; Article 52 addresses retention and destruction. The authority also publishes transfer-contract tools. [DPO, Chapter VII](https://dpo.gov.rw/dpp-law/sharing-transferstorage-and-retention-of-personal-data), [official compliance tools](https://dpo.gov.rw/compliance-tools).

**My inference:** legal/privacy reviewers should determine which provisions apply to this specific arrangement and whether official transfer clauses or authorisations are needed. This generic outline does not replace them. Agreement between the parties alone should not be treated as proof that every applicable legal requirement is satisfied.

## 5. Confidentiality and permitted access

Name each approved user and provider, their task and access period. Permit access only for the stated purpose, with confidentiality commitments, individual accounts and an access log. Keep readings, incident files and identity keys separately restricted where practical. Record changes to the authorised list.

Do not put real utility files, sensitive outputs or identifiers in a public/shared code repository, synced chat sources or unrestricted screenshots. Share findings with the utility through the approved channel. Record a process for legally compelled disclosure and notify the data owner where permitted.

## 6. Transfer, storage and external tools

Specify `[approved transfer channel]`, `[processing devices/locations/countries]`, `[storage locations]`, `[backup locations]`, `[approved cloud/AI providers, if any]` and `[subcontractors]`. Require appropriate encryption, access controls and device protection, with responsibilities stated. Set arrangements for credential management, revoking access and incident response.

Do not assume local files stay local: external analysis services, chat uploads, support logs, cloud backup and remote access must be covered explicitly. No external provider or new country is approved merely by listing it in this outline.

## 7. Retention schedule

Agree both a purpose-related retention period and a specific latest date for each category. Use `[sample review completion/date]`, `[historical trial close/date]`, `[active-copy deletion deadline]`, `[latest backup expiry]` and `[permitted retained aggregate reports]`. Include all canonical exports, row audits, temporary files, warning lists, logs and copied attachments. No indefinite “keep for research” default.

Document any required legal hold, the affected material, its basis, custodian and next review date. Isolate it from further trial use. Review extensions in writing rather than quietly retaining copies.

## 8. Return and deletion

On expiry, termination or an agreed withdrawal instruction: stop processing, revoke access and return/delete the agreed material. Document completion, locations checked, remaining restricted backups/holds and final expiry dates. Apply deletion again if an older backup is restored. Confirm how destruction prevents recovery under the approved method; do not promise immediate backup erasure where the platform cannot provide it.

## 9. Ownership and publication rights

Propose that the utility retains its source-data rights and gives a limited, purpose-specific right to use the agreed files. Define treatment of derived outputs separately from pre-existing Bubble Man code. No broad ownership transfer or perpetual reuse licence is implied.

Require written approval of the **specific** public material, including names/logos, case studies, charts, statistics and any data/code examples. Silence is not approval. Agree review contacts and timing, attribution and how privacy/confidentiality concerns are resolved. Keep failures and limitations in the internal record; publication review must not rewrite the factual result. Unapproved material stays private.

## 10. Results, responsibilities and costs

Define deliverables: compatibility report, locked evaluation record, complete results/limitations and, only if separately approved, shadow-trial report. Agree an investigation budget before results. Staff retain normal operational responsibility; the project does not authorise autonomous diagnosis, repairs or valve/pressure changes.

Record `[staff/data-export effort]`, `[who pays agreed costs]`, `[fees, if any]`, `[support boundaries]` and `[commercial terms outside this trial]`. No performance guarantee or expected savings is established. The trial's decision criteria are agreed experimental/operational targets, not an assertion of utility requirements.

## 11. Problems, termination and changes

Agree the notification contacts/deadlines and action plan for suspected unauthorised access, loss, incorrect data or unsafe operating interpretation, aligned with applicable legal duties. Record suspension/termination rights, treatment of incomplete results and remaining data. Legal reviewers select governing law, dispute process, liability and signature wording.

## Decisions still required

**Unverified / open:** parties and authority; zone/data schedule; personal-data classification and applicable permissions; users/providers/countries; retention/backup deletion dates; publication review; operational and cost responsibilities; evaluation protocol; final legal terms. Completion of this outline is not approval of those choices.

**Verified (local scope):** this draft was prepared without real utility data and was not sent. The [pilot guide](/Users/uwonkundathierryrugira/Bubble-man/PILOT-READINESS.md) and [scoring draft](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/SCORING-DRAFT.md) supply the project context. Existing files remain unchanged.
