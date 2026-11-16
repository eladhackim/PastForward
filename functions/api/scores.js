// GET /api/scores → [{ rhyme_id, yes, no }]  (cached at the edge for 60 s)
// If the database is slow or down: an uncached [] so the page renders without vote counts instead of waiting.
import { json, cached } from "./_shared.js";

export async function onRequestGet(context) {
  return cached(context, 60, async () => {
    const { results } = await context.env.DB
      .prepare("SELECT rhyme_id, SUM(vote = 1) AS yes, SUM(vote = -1) AS no FROM votes GROUP BY rhyme_id")
      .all();
    return json(results, 200, 60);
  }, () => json([]));
}
