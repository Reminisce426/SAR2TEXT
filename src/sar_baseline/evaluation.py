import json
from pathlib import Path


def _direction_metrics(
    query_features, candidate_features, positive_indices, ks, query_batch_size, ranking_depth
):
    import torch

    candidate_count = candidate_features.shape[0]
    max_k = min(max(max(ks), ranking_depth), candidate_count)
    hits = {int(k): 0 for k in ks}
    ranks = []
    rankings = []
    for start in range(0, query_features.shape[0], query_batch_size):
        scores = query_features[start : start + query_batch_size] @ candidate_features.T
        # Stable sorting gives a documented candidate-index tie break.
        order = torch.argsort(scores, dim=1, descending=True, stable=True)
        for local_index in range(order.shape[0]):
            query_index = start + local_index
            expected = set(positive_indices[query_index])
            ranked = order[local_index].tolist()
            best_rank = min(ranked.index(index) + 1 for index in expected)
            ranks.append(best_rank)
            rankings.append(ranked[:max_k])
            for k in hits:
                hits[k] += int(best_rank <= min(k, candidate_count))
    count = len(ranks)
    metrics = {"R@{}".format(k): hits[k] / count for k in sorted(hits)}
    metrics["query_count"] = count
    return metrics, ranks, rankings


def evaluate_bidirectional(
    text_features,
    image_features,
    caption_image_indices,
    ks,
    query_batch_size,
    ranking_depth,
):
    text_positives = [{int(index)} for index in caption_image_indices]
    image_positives = [set() for _ in range(image_features.shape[0])]
    for caption_index, image_index in enumerate(caption_image_indices):
        image_positives[image_index].add(caption_index)

    t2i_metrics, t2i_ranks, t2i_rankings = _direction_metrics(
        text_features, image_features, text_positives, ks, query_batch_size, ranking_depth
    )
    i2t_metrics, i2t_ranks, i2t_rankings = _direction_metrics(
        image_features, text_features, image_positives, ks, query_batch_size, ranking_depth
    )
    recall_values = [
        value
        for metrics in (t2i_metrics, i2t_metrics)
        for key, value in metrics.items()
        if key.startswith("R@")
    ]
    return {
        "metrics": {
            "text_to_image": t2i_metrics,
            "image_to_text": i2t_metrics,
            "mean_recall": sum(recall_values) / len(recall_values),
        },
        "text_to_image": {"ranks": t2i_ranks, "rankings": t2i_rankings},
        "image_to_text": {"ranks": i2t_ranks, "rankings": i2t_rankings},
    }


def write_cases(path, evaluation, manifest, case_count_each):
    path = Path(path)
    cases = []
    directions = (
        (
            "text_to_image",
            manifest.caption_ids,
            manifest.captions,
            manifest.image_ids,
            manifest.image_paths,
        ),
        (
            "image_to_text",
            manifest.image_ids,
            manifest.image_paths,
            manifest.caption_ids,
            manifest.captions,
        ),
    )
    for direction, query_ids, query_values, candidate_ids, candidate_values in directions:
        ranks = evaluation[direction]["ranks"]
        rankings = evaluation[direction]["rankings"]
        ordered_best = sorted(range(len(ranks)), key=lambda index: (ranks[index], index))
        ordered_worst = sorted(range(len(ranks)), key=lambda index: (-ranks[index], index))
        selected = [("best", i) for i in ordered_best[:case_count_each]]
        selected += [("worst", i) for i in ordered_worst[:case_count_each]]
        for group, index in selected:
            cases.append(
                {
                    "direction": direction,
                    "group": group,
                    "query_id": query_ids[index],
                    "query_value": query_values[index],
                    "best_positive_rank": ranks[index],
                    "top_candidate_ids": [candidate_ids[i] for i in rankings[index]],
                    "top_candidate_values": [candidate_values[i] for i in rankings[index]],
                }
            )
    with path.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(case, ensure_ascii=False, sort_keys=True) + "\n")
