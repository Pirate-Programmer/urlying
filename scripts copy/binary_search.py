import hash

def binary_search_df(df, target):
    target_hash = hash.get_crc32(target)  # calculating target hash
    
    left, right = 0, len(df) - 1
    
    while left <= right:
        mid = (left + right) // 2
        mid_val = df.iloc[mid]['hash']
        
        if mid_val == target_hash: 
            return df.iloc[mid] # return full row
        elif mid_val < target_hash:
            left = mid + 1
        else:
            right = mid - 1
    
    return None # not found
