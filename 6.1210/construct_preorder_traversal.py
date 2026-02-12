##################################################
##  Problem 3(d) Constructing Tree Traversals
##################################################
def construct_preorder_traversal(inorder, postorder):
    inorder_hash = dict()
    for index, value in enumerate(inorder):
        inorder_hash[value] = index
    preorder = []
    def recursive_helper(inorder_start, inorder_end, postorder_start, postorder_end):
        if inorder_start > inorder_end or postorder_start > postorder_end:
            return
        else:
            root = postorder[postorder_end]
            preorder.append(root)
            # find split between left and right branches in in_order traversal
            root_index  = inorder_hash[root]
            # split inorder into left and right subtrees
            left_size = root_index - inorder_start

            # inorder left subtree
            inorder_start_l = inorder_start
            inorder_end_l = root_index - 1 #exclude root

            #postorder left subtree
            postorder_start_l = postorder_start
            postorder_end_l = postorder_start + left_size - 1

            # inorder right subtree
            inorder_start_r = root_index + 1
            inorder_end_r = inorder_end 

            # postorder right subtree
            postorder_start_r = postorder_start + left_size
            postorder_end_r = postorder_end - 1 #cut root

            # intialize postorder subtrees
            recursive_helper(inorder_start_l, inorder_end_l, postorder_start_l, postorder_end_l)
            recursive_helper(inorder_start_r, inorder_end_r, postorder_start_r, postorder_end_r)
    recursive_helper(0, len(inorder)-1, 0, len(postorder)-1)
    return preorder