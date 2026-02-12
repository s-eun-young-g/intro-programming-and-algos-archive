def count_paths(L):
    '''
    Input:  L | size-n list of size-n lists
              | each L[i][j] is 'V', '+', or ' ' for virus, upgrade, or empty
    Output: p | number of distinct optimal shortest paths from (0,0) to (n-1,n-1)
                that collect the maximum possible upgrades
    '''

    n = len(L)
    infinity = 100000000
    
    #BFS
    dist = [[infinity] * n for _ in range(n)] # init n by n grid of infinite distances
    dist[0][0] = 0 # starting square
    agenda = [(0,0)] # each agenda item stores tuple (i, j)
    idx = 0
    while idx < len(agenda): # while we still have squares to explore
        i, j = agenda[idx] # get coords
        idx += 1
        d_original = dist[i][j]
        neighbors = [(0,1), (0, -1), (1, 0), (-1, 0)]
        for neighbor in neighbors: 
            delta_i, delta_j = neighbor # move
            n_i, n_j = i + delta_i, j + delta_j # new coords
            if 0 <= n_i < n and 0 <= n_j < n and L[n_i][n_j] != 'V': # in range and not virus
                if dist[n_i][n_j] == infinity: # check if not visited
                    dist[n_i][n_j] = d_original + 1 # distance is just 1 more than distance of original square
                    agenda.append((n_i, n_j))

    # check if exit unreachable
    if dist[n-1][n-1] == infinity:
        return 0

    # DP 
    m = [[-1]*n for _ in range(n)] # best upgrades so far
    t = [[0]*n for _ in range(n)] # counts of shortest paths with that many upgrades (aka optimal paths)
    if L[0][0] == "+": # if we start on an uprgade, best path has 1 upgrade to start with
        m[0][0] = 1
    else:
        m[0][0] = 0 # else just 0
    t[0][0] = 1 # only one optimal path so far

    # we want to look at paths by their distances, so we need to sort by distance:
    all_paths = []
    for i in range(n):
        for j in range(n):
            if dist[i][j] != infinity: # if reachable
                all_paths.append((dist[i][j], i, j)) # we want to sort first by dist
    all_paths.sort()

    for d, i, j in all_paths: # iterate through all our valid paths 
        # use similar process to BFS branching out
        current_upgrade = m[i][j]
        current_count = t[i][j]
        neighbors = [(0,1), (0, -1), (1, 0), (-1, 0)] # hello again neighbors!
        for neighbor in neighbors: 
            delta_i, delta_j = neighbor # move
            n_i, n_j = i + delta_i, j + delta_j # new coords
            if 0 <= n_i < n and 0 <= n_j < n: # yippee in range
                 if dist[n_i][n_j] == dist[i][j] + 1: # but are we on a shortest path...?
                    if L[n_i][n_j] == '+':
                        new_upgrade = current_upgrade + 1
                    else:
                        new_upgrade = current_upgrade
                    # if we found a better upgrade total, update m and t
                    if new_upgrade > m[n_i][n_j]:
                        m[n_i][n_j] = new_upgrade
                        t[n_i][n_j] = current_count
                    # if we found an equally good upgrade total, update t (new optimal path)
                    elif new_upgrade == m[n_i][n_j]:
                        t[n_i][n_j] += current_count
    
    return t[n-1][n-1] # return optimal count path of final square :3

