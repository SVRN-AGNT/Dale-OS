/**
 * Agent Review daily spend cap.
 *
 * Owner, 2026-10-14: guard against runaway review spend. The cap counts every
 * run that may have reached the model in the last 24 hours, so it errs towards
 * stopping a review rather than letting one through uncounted:
 *
 *   - A cancelled run counts. The workflow cancels an in-flight review when a
 *     newer head arrives, and the model may already have been paid by then.
 *   - A run counts until 24 hours after its last update, not its creation: a
 *     run that queued before spending stays counted for a full day after it
 *     spent. A run's spend never comes after its last update.
 *   - A re-run never reaches the model, and neither does a run admitted more
 *     than ADMIT_MAX_AGE_MS after it was created. The review job then has at
 *     most JOB_MAX_MS left to spend, so a run that spent in the last day was
 *     created less than ADMIT_MAX_AGE_MS + JOB_MAX_MS + DAY_MS ago, inside the
 *     LISTING_MS of runs the workflow lists. A fresh workflow_dispatch creates
 *     a new run.
 *   - A listing at GitHub's 1,000-run ceiling may be incomplete, so it caps.
 *
 * Only a skipped run is known never to have reached the model.
 */

export const DAY_MS = 24 * 3600 * 1000;
export const ADMIT_MAX_AGE_MS = 20 * 3600 * 1000;
export const JOB_MAX_MS = 35 * 60 * 1000; // the review job's timeout-minutes
export const LISTING_MS = 48 * 3600 * 1000;
// GitHub returns at most 1,000 runs for a created-filtered listing, so a full one may be missing runs.
export const LISTING_CEILING = 1000;

// The earliest creation time the workflow must list.
export function listingSince(now = Date.now()) {
  return new Date(now - LISTING_MS).toISOString();
}

// runs: this workflow's runs created since listingSince(now). A run still going counts.
export function paidRuns(runs, now) {
  return runs.filter((r) => r.conclusion !== 'skipped'
    && (r.status !== 'completed' || !(Date.parse(r.updated_at) < now - DAY_MS))).length;
}

// self: the current run.
export function capReached({ runs, self, cap, now = Date.now() }) {
  if (!(cap > 0)) return false;
  if (!self || Number(self.run_attempt) !== 1) return true;
  if (!(Date.parse(self.created_at) >= now - ADMIT_MAX_AGE_MS)) return true;
  if (runs.length >= LISTING_CEILING) return true;
  return paidRuns(runs, now) > cap;
}
