import sys
sys.setrecursionlimit(50000)

def dfs(Adj, s, parent = None, order = None):
    if parent is None:
        parent = [None for v in Adj]
        order = []
        parent[s] = s
    for v in Adj[s]:
        if parent[v] is None:
            parent[v] = s
            dfs(Adj, v, parent, order)
    order.append(s)
    return parent, order

def full_dfs(Adj):
    parent = [None for v in Adj]
    order = []
    for v in range(len(Adj)):
        if parent[v] is None:
            parent[v] = v
            dfs(Adj, v, parent, order)
    return parent, order

def find_meeting_point(Adj):
    '''
    inputs:
        Adj - an adjacency list such as [[1,2], [2], []]
    return a meeting point or None if no meeting points exist
    '''
    n = len(Adj)
    Adj_rev = [[] for i in range(n)]
    for v in range(n): # iterate through vertices
        for e in Adj[v]: # iterate through adjacent edges
            Adj_rev[e].append(v)
    
    print(Adj_rev)
    
    # full dfs
    full_dfs_out = full_dfs(Adj_rev)
    l = full_dfs_out[1][-1] # last item of order list

    # dfs on l
    dfs_out = dfs(Adj_rev, l)

    nodes_reached = len(dfs_out[1]) # length of ordered nodes list gives # of nodes visited

    if nodes_reached != n:
        return None
    
    print(l)
    return l

if __name__ == "__main__":
    adj = [[1,2],[2],[]]
    find_meeting_point(adj)