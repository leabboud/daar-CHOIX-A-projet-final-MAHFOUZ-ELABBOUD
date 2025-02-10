def carry_table(pattern):
    #Generates the carry table (partial match table) for a given pattern.
    
    ret = [-1] * len(pattern)
    pos, cnd = 1, 0
    
    while pos < len(pattern):
        if pattern[pos] == pattern[cnd]:
            ret[pos] = ret[cnd]
        else:
            ret[pos] = cnd
            while cnd >= 0 and pattern[pos] != pattern[cnd]:
                cnd = ret[cnd]
        pos += 1
        cnd += 1
    
    return ret

def KMP_search(pattern,text):
    #Uses the KMP algorithm to search for a pattern in a text.
    
    if not pattern or not text:
        return False
    
    T = carry_table(pattern)
    j, k = 0, 0
    
    while j < len(text):
        if pattern[k] == text[j]:
            j += 1
            k += 1
            if k == len(pattern):
                return True
        else:
            k = T[k]
            if k < 0:
                j += 1
                k += 1
    
    return False