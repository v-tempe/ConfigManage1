

class TreeVertex:
    def __init__(self, tree, parent, value=None):
        self.tree = tree
        self.value = value
        self.parent = parent
        self.children = list()
        self.degree = 0
        self.depth = (self.parent.depth + 1) if parent else 0

        #self.tree.loafs.add(self)

        if self.tree.height < self.depth:
            self.tree.height = self.depth

    def __str__(self):
        return f"TreeNode{'{' + self.value.__str__() + '}'}"

    def create_child(self, value):
        new_child = TreeVertex(parent=self, tree=self.tree, value=value)

        self.children.append(new_child)
        #self.tree.loafs.remove(self)

    def has_child(self, value):
        for child in self.children:
            if child.value == value:
                return True
        return False

    def has_child_with_param(self, param_name, param):
        for child in self.children:
            if hasattr(child.value, param_name) and getattr(child.value, param_name) == param:
                return True
        return False

    def get_child_with_param(self, param_name, param):
        for child in self.children:
            if hasattr(child.value, param_name) and getattr(child.value, param_name) == param:
                return child
        raise ValueError(f"No one of cur_vertex' children hasn't a param {param_name}=={param}")

    def print(self):
        for child in self.children:
            print(child, end=" ")
        for child in self.children:
            child.print()


class Tree:
    def __init__(self, root_value=None):
        #self.loafs = set()
        self.height = 1
        self.root = TreeVertex(parent=None, tree=self, value=root_value)
        self.cur_vertex = self.root

    def go_to_parent(self):
        #print(f"going to parent")
        self.cur_vertex = self.cur_vertex.parent

    def go_to_child(self, value):
        #print(f"going to child")
        def get_child_index_by_value(value):
            for i, child in enumerate(self.cur_vertex.children):
                if child.value == value:
                    return i
            return -1
        
        if type(value) == int:
            child_index = value
        else:
            child_index = get_child_index_by_value(value)
            if child_index == -1:
                raise ValueError(f"No children with value {value}")
        self.cur_vertex = self.cur_vertex.children[child_index]

    def go_to_child_with_param(self, param_name: str, param):
        #print(f"going to child with param")
        self.cur_vertex = self.cur_vertex.get_child_with_param(param_name, param)

    def go_to_brother(self, brother_index):
        self.cur_vertex = self.cur_vertex.parent.children[brother_index]

    def go_to_root(self):
        #print(f"{self.cur_vertex.value=}")
        #print(f"going to root")
        self.cur_vertex = self.root

    def go_to_certain_vertex(self, vertex):
        #print(f"going to certain vertex")
        self.cur_vertex = vertex

    def get_children(self):
        return self.cur_vertex.children.copy()

    def in_root(self):
        return self.cur_vertex == self.root

    def get_root(self):
        return self.root

    def print(self):
        print(self.root, end=" ")
        self.root.print()

