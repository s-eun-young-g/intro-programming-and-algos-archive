# Note: resubmitted because I'm curious if I have to manually update the max_rating literally EVERYWHERE, or if 
# the bug was like how I had self.aug_AVL = AVLSet(key=lambda p: (p[0])) so I was rewriting nodes
# that had the same cost but different values
# and after I removed all the updating and reverted back to my old max_rating aug function, I'm passing the 5 test cases
# in the test file and my homemade test cases
# so I'm curious if it'll work for all the test cases
# bc cutting out all the updating makes it SO MUCH simpler

# update it didn't work :( but now I know at least all the work I spent updating wasn't for nothing...

# Use this class to implement your data structure
# Player p is represented as the ordered pair (p.cost, p.rating)
def find_best_helper(T, lower, upper, best_player=(-1, -1)):
    # base case: tree is None
    if T is None:
        return None
    
    cost, rating = T.item

    # too cheap
    if cost < lower:
        return find_best_helper(T.right, lower, upper, best_player)
    
    # too expensive
    if cost > upper:
        return find_best_helper(T.left, lower, upper, best_player)
    
    # in range  

    # this check catches if it's the default (-1, -1), otherwise updates new_best 
    # if our current player is better than the best player passed in
    if rating > best_player[1]:
        new_best = (cost, rating)
    else:
        new_best = best_player

    # check left subtree
    if T.left and max_rating(T.left) > new_best[1]:
        left_best = find_best_helper(T.left, lower, upper, new_best)
        # if left_best beats current best update
        if left_best and left_best[1] > new_best[1]:
            new_best = left_best
    
    # check right subtree
    if T.right and max_rating(T.right) > new_best[1]:
        right_best = find_best_helper(T.right, lower, upper, new_best)
        # if left_best beats current best update
        if right_best and right_best[1] > new_best[1]:
            new_best = right_best
    
    # fully updated by now
    return new_best

class Sportsball:

    # Use this to initialize any data structures you need
    def __init__(self):
        self.aug_AVL = AVLSet(key=lambda p: (p[0], p[1]))

    # Records player p as an option to recruit
    # If p is already an option, this does nothing
    # p :: (num, num)
    # returns nothing
    def insert(self, p):
        self.aug_AVL.insert(p)

    # Removes player p as an option to recruit
    # If p is not an option, this does nothing
    # p :: (num, num)
    # returns nothing
    def delete(self, p):
        self.aug_AVL.delete(p)

    # Among available players with cost in range [m/2, m],
    # finds and outputs a player with the highest rating
    # (or None if no such player exists)
    # m :: num
    # return :: (num, num)
    def find_best(self, m):
        lower = m/2
        upper = m
        return find_best_helper(self.aug_AVL.T, lower, upper)


# Below are implementations of the Set and Sequence interfaces using AVL trees
class AVLSet:
    def __init__(self, key = lambda x: x):
        self.key = key
        self.T = None
    def find(self, x):
        T = find(self.T, x, self.key)
        return None if T is None else T.item
    def insert(self, x):
        self.T = insert(self.T, x, self.key)
    def delete(self, x):
        v, self.T = delete(self.T, x, self.key)
        return v

class AVLSeq:
    def __init__(self):
        self.T = None
    def get_at(self, i):
        return get_at(self.T, i).item
    def set_at(self, i, x):
        self.T = set_at(self.T, i, x)
    def insert_at(self, i, x):
        self.T = insert_at(self.T, i, x)
    def delete_at(self, i):
        v, self.T = delete_at(self.T, i)
        return v

# Basic tree functionality
class Tree:
    def __init__(self, item, left, right):
        self.item = item
        self.left = left
        self.right = right

# Augmentations
def update_max_rating(T):
    if T is None:
        return
    cost, rating = T.item
    T.max_rating = rating
    if T.left: 
        T.max_rating = max(T.max_rating, T.left.max_rating)
    if T.right:
        T.max_rating = max(T.max_rating, T.right.max_rating)    
def max_rating(T):
    if T is None:
        return -1
    # begone infinite recursion pls
    return T.max_rating
def size(T):
    if T is None:
        return 0
    if not hasattr(T, "size"):
        T.size = 1 + size(T.left) + size(T.right)
    return T.size
def height(T):
    if T is None:
        return -1
    if not hasattr(T, "height"):
        T.height = 1 + max(height(T.left), height(T.right))
    return T.height
def skew(T):
    if T is None:
        return 0
    return height(T.right) - height(T.left)

# AVL functionality
def AVL(T):
    # If T is an AVL tree, outputs T
    # Otherwise outputs an AVL tree T' such that:
    # T' contains the same elements as T in the same order, and
    # height(T) - 1 <= height(T') <= height(T)
    # All subtrees of T except possibly T itself must be AVL trees
    # T must have skew -2, -1, 0, 1, or 2
    if skew(T) < -1:
        if skew(T.left) > 0:
            T = Tree(T.item, left_rotate(T.left), T.right)
            # update max rating
            update_max_rating(T.left)
            update_max_rating(T.right)
            update_max_rating(T)
        T = right_rotate(T)
    elif skew(T) > 1:
        if skew(T.right) < 0:
            T = Tree(T.item, T.left, right_rotate(T.right))
            update_max_rating(T.left)
            update_max_rating(T.right)
            update_max_rating(T)
        T = left_rotate(T)
    update_max_rating(T)
    return T
def left_rotate(T):
    # Outputs the tree T' that results from a left-rotation at the root of T
    rotated_tree = Tree(T.right.item, Tree(T.item, T.left, T.right.left), T.right.right)
    # update max rating
    # honestly just updating every time the tree changes idk I don't know precisely where
    # the bugginess is coming from
    # help me please coding gods
    update_max_rating(rotated_tree.left)
    update_max_rating(rotated_tree.right)
    update_max_rating(rotated_tree)
    return rotated_tree
def right_rotate(T):
    # Outputs the tree T' that results from a right-rotation at the root of T
    rotated_tree =Tree(T.left.item, T.left.left, Tree(T.item, T.left.right, T.right))
    # update max rating
    update_max_rating(rotated_tree.left)
    update_max_rating(rotated_tree.right)
    update_max_rating(rotated_tree)
    return rotated_tree

# Traversals
def in_order(T):
    if T:
        yield from in_order(T.left)
        yield T
        yield from in_order(T.right)
def pre_order(T):
    if T:
        yield T
        yield from pre_order(T.left)
        yield from pre_order(T.right)
def post_order(T):
    if T:
        yield from post_order(T.left)
        yield from post_order(T.right)
        yield T

# Sequence operations
def get_at(T, i):
    # Outputs the subtree of T whose root is the element at index i in T
    if i < size(T.left):
        return get_at(T.left, i)
    if i > size(T.left):
        return get_at(T.right, i - 1 - size(T.left))
    return T
def set_at(T, i, x):
    # Outputs the tree that results from replacing the element at index i in T with x
    # i must be in the range 0 <= i < size(T)
    if i < size(T.left):
        return Tree(T.item, set_at(T.left, i, x), T.right)
    if i > size(T.right):
        return Tree(T.item, T.left, set_at(T.right, i - 1 - size(T.left), x))
    return Tree(x, T.left, T.right)
def insert_at(T, i, x):
    # Outputs the AVL tree that results from inserting x at index i in T
    # i must be in the range 0 <= i <= size(T)
    if T is None:
        return Tree(x, None, None)
    if i > size(T.left):
        return AVL(Tree(T.item, T.left, insert_at(T.right, i - 1 - size(T.left), x)))
    return AVL(Tree(T.item, insert_at(T.left, i, x), T.right))
def delete_at(T, i):
    # Outputs a pair (x, T'), where T' is the AVL tree that results from deleting x at index i in T
    # i must be in the range 0 <= i < size(T)
    if i < size(T.left):
        rec = delete_at(T.left, i)
        new_tree = (rec[0], AVL(Tree(T.item, rec[1], T.right)))
        update_max_rating(new_tree[1])
        return new_tree
    if i > size(T.left):
        rec = delete_at(T.right, i - 1 - size(T.left))
        new_tree = (rec[0], AVL(Tree(T.item, T.left, rec[1])))
        update_max_rating(new_tree[1])
        return new_tree
    if not T.left:
        return (T.item, T.right)
    if not T.right:
        return (T.item, T.left)
    rec = delete_at(T.right, 0)
    new_tree = (T.item, AVL(Tree(rec[0], T.left, rec[1])))
    update_max_rating(new_tree[1])
    return new_tree

# BST operations
def find(T, x, key = lambda i: i):
    # Outputs the subtree of T whose root has key x
    # T must have BSP w.r.t. key
    if not T:
        return None
    if key(x) < key(T.item):
        return find(T.left, x, key)
    if key(x) > key(T.item):
        return find(T.right, x, key)
    return T
def insert(T, x, key = lambda i: i):
    # Outputs the AVL tree that results from adding x to T
    # T must have BSP w.r.t. key
    if not T:
        new_tree = Tree(x, None, None)
        # UPDATEEEEEE
        update_max_rating(new_tree.left)
        update_max_rating(new_tree.right)
        update_max_rating(new_tree)
        return new_tree
    if key(x) < key(T.item):
        new_tree = AVL(Tree(T.item, insert(T.left, x, key), T.right))
        update_max_rating(new_tree.left)
        update_max_rating(new_tree.right)
        update_max_rating(new_tree)
        return new_tree
    if key(x) > key(T.item):
        new_tree = AVL(Tree(T.item, T.left, insert(T.right, x, key)))
        update_max_rating(new_tree.left)
        update_max_rating(new_tree.right)
        update_max_rating(new_tree)
        return new_tree
    new_tree = Tree(x, T.left, T.right)
    update_max_rating(new_tree)
    return new_tree
def delete(T, x, key = lambda i: i):
    # Outputs the pair (T', y) where y is the item (if any) in T with key x, and T' is the AVL tree that results from deleting y from T
    # T must have BSP w.r.t. key
    if not T:
        return (None, T)
    if key(x) < key(T.item):
        y, new_left = delete(T.left, x, key)
        new_tree = (y, AVL(Tree(T.item, new_left, T.right)))
        update_max_rating(new_tree[1])
        return new_tree
    if key(x) > key(T.item):
        y, new_right = delete(T.right, x, key)
        new_tree = (y, AVL(Tree(T.item, T.left, new_right)))
        update_max_rating(new_tree[1])
        return new_tree
    return delete_at(T, size(T.left))