from collections import deque
class list_functions:
    def flatten(self, List):
        ### take a list of varied depth
        ### and flatten it! with no recursion
        return reduce(list.__add__, map(lambda x: list(x), [y for y in List]))

    def print_list(self, List):
        stack = [(List, -1)]
        while stack:
            item, level = stack.pop()
            if isinstance(item, list):
                for i in reversed(item):
                    stack.append((i, level+1))
            else:
                print "\t" * level, item

    def max_depth(self, List):
        accessorList = self.subtree_indices(List)
        a_list = self.flatten(accessorList)
        c_max_depth = reduce(lambda x, y: max(x, y), a_list)
        if c_max_depth:
            return max(c_max_depth)
        
    def subtree_indices(self, tree_rep):
        tree = [([], tree_rep)]
        list_of_indexLists = []
        tree_indices = deque()
        while tree != []:
            (indices, sub_tree) = tree.pop(0)
            #print indices, sub_tree
            list_of_indexLists.append(indices)
            for (ordinal, subTree) in enumerate(sub_tree[1:]):
                debug(ordinal)
                debug(subTree)
                if isinstance(subTree, list):
                    idxs = indices[:]

                    debug(idxs)
                    debug(ordinal)

                    if len(idxs) == 0:
                        tree_indices.append([0])
                    else:
                        tree_indices.append(idxs)

                    idxs.append(ordinal+1)
                    tree.append((idxs, subTree))

        return list_of_indexLists
