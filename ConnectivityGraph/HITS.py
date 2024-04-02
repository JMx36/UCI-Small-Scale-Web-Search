def compute_hits(graph, max_iter=50, tolerance=1e-2):
    # Initialize authority and hub scores
    authority_scores = {page: 1 for page in graph}
    hub_scores = {page: 1 for page in graph}

    for _ in range(max_iter):

        # Update hub scores based on incoming links
        new_authority_scores = {page: sum(hub_scores[in_page] for in_page in links["incoming"]) for page, links in graph.items()}
            
        # Update hub scores based on outgoing links
        new_hub_scores = {page: sum(authority_scores[out_page] for out_page in links["outgoing"]) for page, links in graph.items()}

        # Normalize scores
        norm = sum(score ** 2 for score in new_authority_scores.values()) ** 0.5
        new_authority_scores = {page: score / norm for page, score in new_authority_scores.items()}
        norm = sum(score ** 2 for score in new_hub_scores.values()) ** 0.5
        new_hub_scores = {page: score / norm for page, score in new_hub_scores.items()}

        # Check for convergence
        if all(abs(new_hub_scores[page] - hub_scores[page]) < tolerance and \
                abs(new_authority_scores[page] - authority_scores[page]) < tolerance for page in graph):
            break

        hub_scores, authority_scores = new_hub_scores, new_authority_scores

    return hub_scores, authority_scores
