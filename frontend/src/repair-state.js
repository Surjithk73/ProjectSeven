// Kept separate so evidence handling can be checked without rendering a browser.
export function repairPresentation(state) {
  const validated = ['validated', 'pr_opened'].includes(state.agent_status);
  const score = state.ips_score;
  return { validated, score: Number.isInteger(score) && score >= 0 && score <= 100 ? score : null };
}
