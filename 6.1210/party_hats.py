##################################################
##  Problem 3(c): Psyduck's Party Hats
##################################################

# Given n distinct integers in the range [0,N] where n <= N, find an integer
# in the range [0,N] that is missing. If there are multiple missing numbers,
# return any of them. There is at least one number in the range that is missing.
def find_missing_hat(A, N):
    '''
    Inputs:
        A       (list(int)) | List of unsorted, unique non-negative integers
        N       (int)       | A positive integer at least as large as len(A)
    Output:
        -       (int)       | An integer in the range [0,N] not present in arr
    '''
    # wait i didn't use N anywhere I'm just seeing it's an argument? I should start looking at
    # these templates like before I start coding?
    # well time to test
    # we'll see what happens
    # I don't think anyone reads these drafted notes
    # if you do hello, sorry about the nonsense
    # it's late i'm crazy i'm talking to myself

    # part (a): partitioning algorithm

    # initialize i and j
    i = 0
    j = len(A) - 1

    # partition around length of A
    m = len(A)
    
    while i <= j:
        if A[i] >= m and A[j] < m:
            A[i], A[j] = A[j], A[i]
            i += 1
            j -= 1
            pass
        elif A[i] >= m and A[j] >= m:
            j -= 1
            pass
        elif A[i] < m and A[j] < m:
            i += 1
            pass
        elif A[i] < m and A[j] >= m:
            i += 1
            j -= 1
            pass
    
    # we can just deal with the lower half
    A2 = A[:i]
    
    # initialize new pointer
    i2 = 0

    # now, swap numbers to match their indices
    while i2 < i:
        matching_index = A2[i2]
        # keep swapping if: we're in range and we're still not matched
        if 0 <= matching_index and matching_index < i and A2[i2] != i2 and A2[i2] != A2[matching_index]:
            A2[i2], A2[matching_index] = A2[matching_index], A2[i2]
        else:
        # we're matched or we have nowhere to swap that number to (out of range)
            i2 += 1 # move on
        
    i3 = 0
    # scan for the unmatched index—the index in unmatched because we didn't find its corresponding
    # number anywhere to swap into its place, so that hat is missing!
    for i3 in range(len(A2)):
        if A2[i3] != i3:
            return i3
    
    # well, the missing hat has to be where we partitioned if we haven't found it (length of A)
    return i