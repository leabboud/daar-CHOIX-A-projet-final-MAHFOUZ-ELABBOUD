class RegExTree:
    #Represents a node in the regular expression syntax tree.
    
    CONCAT = 0xC04CA7
    ETOILE = 0xE7011E
    ALTERN = 0xA17E54
    PROTECTION = 0xBADDAD
    PARENTHESEOUVRANT = 0x16641664
    PARENTHESEFERMANT = 0x51515151
    DOT = 0xD07

    def __init__(self, root, sub_trees=None):
        self.root = root
        self.sub_trees = sub_trees if sub_trees is not None else []

    def __str__(self):
        if not self.sub_trees:
            return self.root_to_string()
        result = f"{self.root_to_string()}({self.sub_trees[0]}"
        for sub_tree in self.sub_trees[1:]:
            result += f",{sub_tree}"
        return result + ")"

    def root_to_string(self):
        if self.root == self.CONCAT:
            return "."
        if self.root == self.ETOILE:
            return "*"
        if self.root == self.ALTERN:
            return "|"
        if self.root == self.DOT:
            return "."
        return chr(self.root)


class RegExParser:
    #Parses a given regex string and constructs a syntax tree.
    
    reg_ex = ""

    @staticmethod
    def set_reg_ex(regex_pattern):
        RegExParser.reg_ex = regex_pattern

    @staticmethod
    def parse():
        if not RegExParser.reg_ex:
            raise Exception("Empty regex pattern")
        result = [RegExTree(RegExParser.char_to_root(c)) for c in RegExParser.reg_ex]
        return RegExParser._parse(result)

    @staticmethod
    def char_to_root(c):
        if c == '.':
            return RegExTree.DOT
        if c == '*':
            return RegExTree.ETOILE
        if c == '|':
            return RegExTree.ALTERN
        if c == '(':
            return RegExTree.PARENTHESEOUVRANT
        if c == ')':
            return RegExTree.PARENTHESEFERMANT
        return ord(c)

    @staticmethod
    def _parse(result):
        while RegExParser._contain_parentheses(result):
            result = RegExParser._process_parentheses(result)
        while RegExParser._contain_etoile(result):
            result = RegExParser._process_etoile(result)
        while RegExParser._contain_concat(result):
            result = RegExParser._process_concat(result)
        while RegExParser._contain_altern(result):
            result = RegExParser._process_altern(result)
        if len(result) > 1:
            raise Exception("Parsing Error: Multiple roots found")
        return RegExParser._remove_protection(result[0])

    @staticmethod
    def _contain_parentheses(trees):
        return any(t.root in {RegExTree.PARENTHESEFERMANT, RegExTree.PARENTHESEOUVRANT} for t in trees)

    @staticmethod
    def _process_parentheses(trees):
        result, found = [], False
        for t in trees:
            if not found and t.root == RegExTree.PARENTHESEFERMANT:
                content, done = [], False
                while result and not done:
                    if result[-1].root == RegExTree.PARENTHESEOUVRANT:
                        done = True
                        result.pop()
                    else:
                        content.insert(0, result.pop())
                if not done:
                    raise Exception("Mismatched parentheses")
                found = True
                result.append(RegExTree(RegExTree.PROTECTION, [RegExParser._parse(content)]))
            else:
                result.append(t)
        if not found:
            raise Exception("Mismatched parentheses")
        return result

    @staticmethod
    def _contain_etoile(trees):
        return any(t.root == RegExTree.ETOILE and not t.sub_trees for t in trees)

    @staticmethod
    def _process_etoile(trees):
        result, found = [], False
        for t in trees:
            if not found and t.root == RegExTree.ETOILE and not t.sub_trees:
                if not result:
                    raise Exception("Invalid use of * operator")
                found = True
                result.append(RegExTree(RegExTree.ETOILE, [result.pop()]))
            else:
                result.append(t)
        return result

    @staticmethod
    def _contain_concat(trees):
        first_found = False
        for t in trees:
            if not first_found and t.root != RegExTree.ALTERN:
                first_found = True
                continue
            if first_found and t.root != RegExTree.ALTERN:
                return True
            first_found = False
        return False

    @staticmethod
    def _process_concat(trees):
        result, found, first_found = [], False, False
        for t in trees:
            if not found and not first_found and t.root != RegExTree.ALTERN:
                first_found = True
                result.append(t)
                continue
            if not found and first_found and t.root == RegExTree.ALTERN:
                first_found = False
                result.append(t)
                continue
            if not found and first_found and t.root != RegExTree.ALTERN:
                found = True
                result.append(RegExTree(RegExTree.CONCAT, [result.pop(), t]))
            else:
                result.append(t)
        return result

    @staticmethod
    def _contain_altern(trees):
        return any(t.root == RegExTree.ALTERN and not t.sub_trees for t in trees)

    @staticmethod
    def _process_altern(trees):
        result, found, left = [], False, None
        for t in trees:
            if not found and t.root == RegExTree.ALTERN and not t.sub_trees:
                if not result:
                    raise Exception("Invalid use of | operator")
                found = True
                left = result.pop()
                continue
            if found:
                result.append(RegExTree(RegExTree.ALTERN, [left, t]))
                found = False
            else:
                result.append(t)
        return result

    @staticmethod
    def _remove_protection(tree):
        if tree.root == RegExTree.PROTECTION:
            return tree.sub_trees[0] if tree.sub_trees else tree
        tree.sub_trees = [RegExParser._remove_protection(t) for t in tree.sub_trees]
        return tree
