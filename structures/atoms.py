from collections import deque

## Original: http://www.ece.arizona.edu/~denny/python_nest/graph_lib_1.0.1.html
## Modifications: Alex Toney
class Queue:
    def __init__(self):
        self.queue = deque()

    def empty(self):
        if(len(self.queue) > 0):
            return False
        else:
            return True

    def count(self):
        return len(self.queue)

    def add(self, item):
        self.queue.append(item)	

    def remove(self):
        item = self.queue[0]
        self.queue = self.queue[1:]
        return item

class Stack:
    def __init__(self):
        self.s=[]

    def empty(self):
        if(len(self.s)>0):
            return 0
        else:
            return 1

    def count(self):
        return len(self.s)

    def push(self, item):
        ts=[item]
        for i in self.s:
            ts.append(i)
        self.s=ts

    def pop(self):
        item=self.s[0]
        self.s=self.s[1:]
        return item


class GraphException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Atoms:
    ## Atoms are a basic hypergraph
    def __init__(self):
        self.next_edge_id = 0
        self.nodes = {}
        self.edges = {}
        self.hidden_edges = {}
        self.hidden_nodes = {}


    #--Performs a copy of the graph, G, into self.
    #--hidden edges and hidden nodes are not copied.
    #--node_id's remain consistent across self and G, 
    #--however edge_id's do not remain consistent.
    #--Need to implement copy operator on node_data
    #--and edge data.
    def copy(self, G):
        #--Blank self.
        self.nodes = {}
        self.edges = {}
        self.hidden_edges = {}
        self.hidden_nodes = {}
        self.next_edge_id = 0
        #--Copy nodes.
        G_node_list = G.node_list()
        for G_node in G_node_list:
            self.add_node(G_node,G.node_data(G_node))
        #--Copy edges.
        for G_node in G_node_list:
            out_edges = G.out_arcs(G_node)
            for edge in out_edges:
                tail_id=G.tail(edge)
                self.add_edge(G_node, tail_id, G.edge_data(edge))

    #--Creates a new node with id node_id.  Arbitrary data can be attached
    #--to the node via the node_data parameter.
    def add_node(self, node_id, node_data=None, ignore_dupes=False):
        if (not self.nodes.has_key(node_id)) and (not self.hidden_nodes.has_key(node_id)):
            self.nodes[node_id]=([],[],node_data)
        else:
            if not ignore_dupes:
                raise GraphException('Duplicate Node: %s', node_id)

    #--Deletes the node and all in and out arcs.
    def delete_node(self, node_id):
        #--Remove fanin connections.
        in_edges=self.in_arcs(node_id)
        for edge in in_edges:
            self.delete_edge(edge)
        #--Remove fanout connections.
        out_edges = self.out_arcs(node_id)
        for edge in out_edges:
            self.delete_edge(edge)
        #--Delete node.
        del self.nodes[node_id]

    #--Delets the edge.
    def delete_edge(self, edge_id):
        head_id = self.head(edge_id)
        tail_id = self.tail(edge_id)
        head_data = map(None, self.nodes[head_id])
        tail_data = map(None, self.nodes[tail_id])
        head_data[1].remove(edge_id)
        tail_data[0].remove(edge_id)
        del self.edges[edge_id]

    #--Adds an edge (head_id, tail_id).
    #--Arbitrary data can be attached to the edge via edge_data
    def add_edge(self, head_id, tail_id, edge_data=None):
        edge_id = self.next_edge_id
        self.next_edge_id = self.next_edge_id + 1
        self.edges[edge_id] = (head_id, tail_id, edge_data)
        try:
            mapped_head_data = map(None, self.nodes[head_id])
            mapped_head_data[1].append(edge_id)
            mapped_tail_data = map(None, self.nodes[tail_id])
            mapped_tail_data[0].append(edge_id)
        except Exception, E:
            raise GraphException('Exception %s nodes: %s' % (E, self.nodes))
        
        return edge_id

    #--Removes the edge from the normal graph, but does not delete
    #--its information.  The edge is held in a separate structure
    #--and can be unhidden at some later time.
    def hide_edge(self, edge_id):
        self.hidden_edges[edge_id]=self.edges[edge_id]
        ed=map(None, self.edges[edge_id])
        head_id=ed[0]
        tail_id=ed[1]
        hd=map(None, self.nodes[head_id])
        td=map(None, self.nodes[tail_id])
        hd[1].remove(edge_id)
        td[0].remove(edge_id)
        del self.edges[edge_id]

    #--Similar to above.
    #--Stores a tuple of the node data, and the edges that are incident to and from
    #--the node.  It also hides the incident edges.
    def hide_node(self, node_id):	    
        degree_list = self.arc_list(node_id)
        self.hidden_nodes[node_id] = (self.nodes[node_id],degree_list)
        for edge in degree_list:
            self.hide_edge(edge)
        del self.nodes[node_id]

    #--Restores a previously hidden edge back into the graph.
    def restore_edge(self, edge_id):
        self.edges[edge_id] = self.hidden_edges[edge_id]
        ed = map(None,self.hidden_edges[edge_id])
        head_id = ed[0]
        tail_id = ed[1]
        hd=map(None,self.nodes[head_id])
        td=map(None,self.nodes[tail_id])
        hd[1].append(edge_id)
        td[0].append(edge_id)
        del self.hidden_edges[edge_id]

    #--Restores all hidden edges.
    def restore_all_edges(self):
        hidden_edge_list=self.hidden_edges.keys()
        for edge in hidden_edge_list:
            self.restore_edge(edge)

    #--Restores a previously hidden node back into the graph
    #--and restores all of the hidden incident edges, too.	
    def restore_node(self, node_id):
        hidden_node_data=map(None,self.hidden_nodes[node_id])
        self.nodes[node_id]=hidden_node_data[0]
        degree_list=hidden_node_data[1]
        for edge in degree_list:
            self.restore_edge(edge)
        del self.hidden_nodes[node_id]

    #--Restores all hidden nodes.
    def restore_all_nodes(self):
        hidden_node_list=self.nodes.keys()
        for node in hidden_node_list:
            self.nodes[node]=self.hidden_nodes[node]
            del self.hidden_nodes[node]

    #--Returns 1 if the node_id is in the graph and 0 otherwise.
    def has_node(self, node_id):
        if self.nodes.has_key(node_id):
            return 1
        else:
            return 0

    #--Returns the edge that connects (head_id,tail_id)
    def edge(self, head_id, tail_id):
        out_edges=self.out_arcs(head_id)
        for edge in out_edges:
            if self.tail(edge) == tail_id:
                return edge
        raise 'Graph_no_edge', (head_id, tail_id)
        #print "WARNING: No edge to return."
        
    def neighbors(self, node_id):
        return self.out_arcs(node_id)
        
    def number_of_nodes(self):
        return len(self.nodes.keys())

    def number_of_edges(self):
        return len(self.edges.keys())

    #--Return a list of the node id's of all visible nodes in the graph.
    def node_list(self):
        nl = self.nodes.keys()
        return nl[:]	

    #--Similar to above.
    def edge_list(self):
        el = self.edges.keys()
        return el[:]

    def number_of_hidden_edges(self):
        return len(self.hidden_edges.keys())

    def number_of_hidden_nodes(self):
        return len(self.hidden_nodes.keys())

    def hidden_node_list(self):
        hnl=self.hidden_nodes.keys()
        return hnl[:]

    def hidden_edge_list(self):
        hel=self.hidden_edges.keys()
        return hel[:]

    #--Returns a reference to the data attached to a node.
    def node_data(self, node_id):
        mapped_data=map(None, self.nodes[node_id])
        return mapped_data[2]

    #--Returns a reference to the data attached to an edge.
    def edge_data(self, edge_id):
        mapped_data=map(None, self.edges[edge_id])
        return mapped_data[2]

    #--Returns a reference to the head of the edge.  (A reference to the head id)
    def head(self, edge):
        mapped_data = map(None, self.edges[edge])
        return mapped_data[0]	

    #--Similar to above.
    def tail(self, edge):
        mapped_data=map(None, self.edges[edge])
        return mapped_data[1]

    #--Returns a copy of the list of edges of the node's out arcs.
    def out_arcs(self, node_id):
        mapped_data = map(None, self.nodes[node_id])
        return mapped_data[1][:]	

    #--Similar to above.
    def in_arcs(self, node_id):
        mapped_data = map(None, self.nodes[node_id])
        return mapped_data[0][:]

    def arc_pairs(self, node_id):
        for x in self.in_arcs(node_id):
            for y in self.out_arcs(node_id):
                yield (x,y)
        
    #--Returns a list of in and out arcs.
    def arc_list(self, node_id):
        in_list  = self.in_arcs(node_id)
        out_list = self.out_arcs(node_id)
        deg_list = []
        for arc in in_list:
            deg_list.append(arc)
        for arc in out_list:
            deg_list.append(arc)
        return deg_list


    def out_degree(self, node_id):
        mapped_data = map(None, self.nodes[node_id])
        return len(mapped_data[1])

    def in_degree(self, node_id):
        mapped_data = map(None, self.nodes[node_id])
        return len(mapped_data[0])

    def degree(self, node_id):
        mapped_data=map(None, self.nodes[node_id])
        return len(mapped_data[0])+len(mapped_data[1])	

    def is_cyclic(self):
        pass
    
    # --- Traversals ---

    #--Performs a topological sort of the nodes by "removing" nodes with indegree 0.
    #--If the graph has a cycle, the Graph_topological_error is thrown with the
    #--list of successfully ordered nodes.
    def topological_sort(self):
        topological_list  = []
        topological_queue = Queue()
        indeg_nodes = {}
        node_list=self.nodes.keys()
        for node in node_list:
            indeg = self.in_degree(node)
            if indeg == 0:
                topological_queue.add(node)
            else:
                indeg_nodes[node]=indeg
        while not topological_queue.empty():
            current_node = topological_queue.remove()
            topological_list.append(current_node)
            out_edges = self.out_arcs(current_node)
            for edge in out_edges:
                tail = self.tail(edge)
                indeg_nodes[tail] = indeg_nodes[tail]-1
                if indeg_nodes[tail] == 0:
                    topological_queue.add(tail)
        #--Check to see if all nodes were covered.
        if len(topological_list) != len(node_list):
            raise GraphException(topological_list)
        return topological_list

    #--Performs a reverse topological sort by iteratively "removing" nodes with out_degree=0
    #--If the graph is cyclic, this method throws Graph_topological_error with the list of
    #--successfully ordered nodes.
    def reverse_topological_sort(self):
        topological_list  = []
        topological_queue = Queue()
        outdeg_nodes = {}
        node_list = self.nodes.keys()
        for node in node_list:
            outdeg = self.out_degree(node)
            if outdeg == 0:
                topological_queue.add(node)
            else:
                outdeg_nodes[node] = outdeg
        while not topological_queue.empty():
            current_node = topological_queue.remove()
            topological_list.append(current_node)			
            in_edges = self.in_arcs(current_node)
            for edge in in_edges:
                head_id = self.head(edge)
                outdeg_nodes[head_id] = outdeg_nodes[head_id]-1
                if outdeg_nodes[head_id] == 0:
                    topological_queue.add(head_id)
        #--Sanity check.
        if len(topological_list) != len(node_list):
            raise Graph_topological_error, topological_list
        return topological_list

    #--Returns a list of nodes in some DFS order.
    def dfs(self, source_id):
        nodes_already_stacked = {source_id:0}
        dfs_list  = []		
        dfs_stack = Stack()

        dfs_stack.push(source_id)

        while not dfs_stack.empty():
            current_node = dfs_stack.pop()
            dfs_list.append(current_node)
            out_edges = self.out_arcs(current_node)
            for edge in out_edges:
                if not nodes_already_stacked.has_key(self.tail(edge)):
                    nodes_already_stacked[self.tail(edge)] = 0
                    dfs_stack.push(self.tail(edge))
                    
        return dfs_list

    #--Returns a list of nodes in some BFS order.
    def bfs(self, source_id):
        nodes_already_queued={source_id:0}
        bfs_list  = []
        bfs_queue = Queue()
        bfs_queue.add(source_id)	

        while not bfs_queue.empty():
            current_node = bfs_queue.remove()
            bfs_list.append(current_node)
            out_edges = self.out_arcs(current_node)
            for edge in out_edges:
                if not nodes_already_queued.has_key(self.tail(edge)):
                    nodes_already_queued[self.tail(edge)]=0
                    bfs_queue.add(self.tail(edge))
                    
        return bfs_list


    #--Returns a list of nodes in some BACKWARDS BFS order.
    #--Starting from the source node, BFS proceeds along back edges.
    def back_bfs(self, source_id):
        nodes_already_queued = {source_id:0}
        bfs_list  = []
        bfs_queue = Queue()
        bfs_queue.add(source_id)

        while not bfs_queue.empty():
            current_node = bfs_queue.remove()
            bfs_list.append(current_node)
            in_edges = self.in_arcs(current_node)
            for edge in in_edges:
                if not nodes_already_queued.has_key(self.head(edge)):
                    nodes_already_queued[self.head(edge)]=0
                    bfs_queue.add(self.head(edge))

        return bfs_list
