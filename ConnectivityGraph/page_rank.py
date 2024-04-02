def compute_pagerank(graph, alpha=0.85, max_iterations=100, tolerance=1e-2):
    # computes the pageRank scores for the graph
    num_pages = len(graph)
    # initializes pageRank scores equally among all pages
    pagerank_scores = {page: 1.0 / num_pages for page in graph}
    for _ in range(max_iterations): # _ for loop not being used here
        new_scores = pagerank_scores.copy()
        for page, links in graph.items():
            incoming_links = links['incoming']  # Use 'incoming' key for accessing incoming links
            new_score = (1 - alpha) / num_pages
            new_score += alpha * sum(pagerank_scores[link] / len(graph[link]['outgoing']) for link in incoming_links)  # Use 'outgoing' key for outgoing links
            new_scores[page] = new_score

        # Check for convergence
        if all(abs(new_scores[page] - pagerank_scores[page]) < tolerance for page in pagerank_scores):
            break
        pagerank_scores = new_scores

    # Normalize scores        
    total_score = sum(pagerank_scores.values())
    pagerank_scores = {page: pagerank_scores[page]/total_score for page in pagerank_scores}

    return pagerank_scores