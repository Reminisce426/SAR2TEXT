def _validate_scores(scores, candidate_count):
    rows = [list(row) for row in scores]
    if not rows:
        raise ValueError("At least one query is required")
    if any(len(row) != candidate_count for row in rows):
        raise ValueError("Every score row must match candidate_count")
    return rows


def stable_ranking(score_row):
    """Rank descending by score, resolving ties by lower candidate index."""
    return sorted(range(len(score_row)), key=lambda index: (-score_row[index], index))


def recall_from_scores(scores, positives, candidate_count, ks=(1, 5, 10)):
    """Reference implementation used by tests and small evaluations.

    positives is an iterable of candidate-index iterables, one per query.
    """
    rows = _validate_scores(scores, candidate_count)
    positive_sets = [set(items) for items in positives]
    if len(rows) != len(positive_sets):
        raise ValueError("scores and positives must have the same query count")
    if any(not items for items in positive_sets):
        raise ValueError("Every query must have at least one positive candidate")
    if any(index < 0 or index >= candidate_count for items in positive_sets for index in items):
        raise ValueError("Positive candidate index is out of range")

    hits = {int(k): 0 for k in ks}
    ranks = []
    rankings = []
    for row, expected in zip(rows, positive_sets):
        ranking = stable_ranking(row)
        rankings.append(ranking)
        best_rank = min(ranking.index(index) + 1 for index in expected)
        ranks.append(best_rank)
        for k in hits:
            if best_rank <= min(k, candidate_count):
                hits[k] += 1
    query_count = len(rows)
    result = {"R@{}".format(k): hits[k] / query_count for k in sorted(hits)}
    result["query_count"] = query_count
    return result, ranks, rankings


def bidirectional_recall(scores_text_to_image, caption_image_indices, ks=(1, 5, 10)):
    """Compute text-to-image and image-to-text metrics with multi-caption positives."""
    caption_image_indices = list(caption_image_indices)
    image_count = max(caption_image_indices) + 1 if caption_image_indices else 0
    caption_count = len(caption_image_indices)
    if image_count == 0:
        raise ValueError("At least one image-caption pair is required")
    text_positives = [{image_index} for image_index in caption_image_indices]
    text_metrics, text_ranks, text_rankings = recall_from_scores(
        scores_text_to_image, text_positives, image_count, ks
    )

    image_scores = [
        [scores_text_to_image[caption_index][image_index] for caption_index in range(caption_count)]
        for image_index in range(image_count)
    ]
    image_positives = [
        {caption_index for caption_index, owner in enumerate(caption_image_indices) if owner == image_index}
        for image_index in range(image_count)
    ]
    image_metrics, image_ranks, image_rankings = recall_from_scores(
        image_scores, image_positives, caption_count, ks
    )
    return {
        "text_to_image": text_metrics,
        "image_to_text": image_metrics,
        "text_ranks": text_ranks,
        "image_ranks": image_ranks,
        "text_rankings": text_rankings,
        "image_rankings": image_rankings,
    }
