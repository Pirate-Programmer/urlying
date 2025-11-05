import math,os, re, json, time
from collections import Counter
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

def is_https(url):
    try:
        if url.startswith("https://"):
            return 1
        elif url.startswith("http://"):
            return 0
        else:
            raise ValueError("Invalid URL: must start with http:// or https://")
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def url_length(url):
    try:
        return len(url)  
    except Exception as e:
        print(f"{e}")
        return None
    
def domain_length(url):
    try:
        if url.startswith("https://"):
            url = url[8:]
        elif url.startswith("http://"):
            url = url[7:]
        else:
            raise ValueError("Invalid URL: must start with http:// or https://")
        
        domain = url.split('/')[0].split(':')[0]
        if domain.startswith("www."):
            domain = domain[4:]
        return domain, len(domain)
    except Exception as e:
        print(f"Error: {e}")
        return None, 0
    
def path_length(url):
    try:
        if url.startswith("https://"):
            url = url[8:]
        elif url.startswith("http://"):
            url = url[7:]
        else:
            raise ValueError("Invalid URL: must start with http:// or https://")

        parts = url.split('/', 1)

        if len(parts) == 1:
            return "/", 0

        path_part = parts[1]
        path = path_part.split('?', 1)[0].split('#', 1)[0]

        if path.strip() == "":
            return "/", 0

        clean_path = '/' + path
        return clean_path, len(clean_path)

    except Exception as e:
        print(f"Error: {e} | URL: {url}")
        return None, 0
    
def path_depth(path):
    try:
        if path == "/":
            return 0
            
        parts = [p for p in path.split('/') if p]
        return len(parts)
    except Exception as e:
        print(f"Error: {e} | Path: {path}")
        return 0
    
def query_length_and_count(url):
    try:
        if '?' not in url:
            return "?", 0, 0

        query_part = url.split('?', 1)[1]
        query = query_part.split('#', 1)[0]

        if query.strip() == "":
            return "?", 0, 0

        query_length = len(query)
        query_count = len(query.split('&'))

        return query, query_length, query_count
        
    except Exception as e:
        print(f"Error: {e} | URL: {url}")
        return None, 0, 0

def fragment_length(url):
    try:
        if '#' not in url:
            return "#", 0

        fragment = url.split('#', 1)[1]

        if fragment.strip() == "":
            return "#", 0

        return fragment, len(fragment)

    except Exception as e:
        print(f"Error: {e} | URL: {url}")
        return None, 0
    
def shannon_entropy(text):
    try:
        if not text:
            return 0.0

        freq = Counter(text)
        length = len(text)

        entropy = 0.0
        for count in freq.values():
            p = count / length
            entropy -= p * math.log2(p)

        return round(entropy, 2)

    except Exception as e:
        print(f"Error: {e}")
        return 0.0
    
def count_dots(url):
    try:
        return url.count('.')
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_at_symbols(url):
    try:
        return url.count('@')
    except Exception as e:
        print(f"Error: {e}")
        return 0

def count_equals(url):
    try:
        return url.count('=')
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_special_chars(url):
    try:
        return len(re.findall(r'[^a-zA-Z0-9./@=:%\-&~?_]', url))
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_slashes(url):
    try:
        return url.count('/')
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_hyphens(url):
    try:
        return url.count('-')
    except Exception as e:
        print(f"Error: {e}")
        return 0

def count_digits(url):
    try:
        return sum(c.isdigit() for c in url)
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_colons(url):
    try:
        return url.count(':')
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_qm(url):
    try:
        return url.count('?')
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_and(url):
    try:
        return url.count('&')
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_underscore(url):
    try:
        return url.count('_')
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_tilde(url):
    try:
        return url.count('~')
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_percent(url):
    try:
        return url.count('%')
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_lowercase_letters(url):
    try:
        return sum(1 for c in url if c.islower())
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_uppercase_letters(url):
    try:
        return sum(1 for c in url if c.isupper())
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def upper_to_lower_ratio(upper, lower):
    try:
        if lower == 0:
            return round(upper, 2) if upper != 0 else 0.0 
        return round(upper / lower, 2)
    except Exception as e:
        print(f"Error: {e} | upper: {upper}, lower: {lower}")
        return 0.0
    
def is_domain_ip(domain):
    try:
        parts = str(domain).split('.')
        if len(parts) != 4:
            return 0

        for part in parts:
            if not part.isdigit():
                return 0
            num = int(part)
            if num < 0 or num > 255:
                return 0

        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 0
    
def count_subdomains(domain, is_domain_ip):
    try:
        if is_domain_ip == 1:
            return 0  
        parts = domain.strip().split('.')
        if len(parts) <= 2:
            return 0 
        return len(parts) - 2
    except Exception as e:
        print(f"Error: {e} | Domain: {domain}")
        return 0
    
def character_transition_entropy(text):
    try:
        if not text or len(text) < 2:
            return 0.0

        bigrams = [text[i:i+2] for i in range(len(text)-1)]
        total = len(bigrams)

        freq = Counter(bigrams)
        entropy = 0.0
        for count in freq.values():
            p = count / total
            entropy -= p * math.log2(p)

        return round(entropy, 2)

    except Exception as e:
        print(f"Error: {e}")
        return 0.0
    
def digit_to_length_ratio(digits, url_length):
    try:
        if url_length == 0:
            return 0.0
        return round(digits / url_length, 2)
    except Exception as e:
        print(f"Error: {e}")
        return 0.0
    
def char_to_length_ratio(al_count, url_length):
    try:
        if url_length == 0:
            return 0.0
        return round(al_count / url_length, 2)
    except Exception as e:
        print(f"Error: {e}")
        return 0.0
    
def specialchar_to_length_ratio(special_count, url_length):
    try:
        if url_length == 0:
            return 0.0
        return round(special_count / url_length, 2)
    except Exception as e:
        print(f"Error: {e}")
        return 0.0

def extract_tld(domain, is_ip):
    try:
        if is_ip == 1:
            return "Absent"

        parts = domain.split('.')
        if len(parts) < 2:
            return "Invalid"

        return parts[-1].lower()
    except Exception as e:
        print(f"Error: {e}")
        return ""
    
def check_tld_and_mtld(domain, tld_set):
    try:
        domain = domain.strip().lower()
        parts = domain.split('.')

        if len(parts) < 2:
            return 0, 0 

        tld = parts[-1]
        mtld = parts[-2]

        return int(tld in tld_set), int(mtld in tld_set)

    except Exception as e:
        print(f"Error: {e}")
        return 0, 0
    
def extract_features_for_url(url: str) -> Dict[str, Any]:
    tlds = pd.read_csv("../datasets/tlds/tlds.csv")
    # basic parts
    https_flag = is_https(url)
    u_len = url_length(url)
    domain, domain_len = domain_length(url)
    path, path_len = path_length(url)
    path_dep = path_depth(path)
    query, query_len, query_count = query_length_and_count(url)
    fragment, fragment_len = fragment_length(url)

    # counts
    dots = count_dots(url)
    at_symbols = count_at_symbols(url)
    equals = count_equals(url)
    special_chars = count_special_chars(url)
    slashes = count_slashes(url)
    hyphens = count_hyphens(url)
    digits = count_digits(url)
    colons = count_colons(url)
    qm = count_qm(url)
    ands = count_and(url)
    underscores = count_underscore(url)
    tildes = count_tilde(url)
    percents = count_percent(url)
    lower = count_lowercase_letters(url)
    upper = count_uppercase_letters(url)
    al_count = lower + upper

    # derived / ratios / entropy
    upper_lower_ratio = upper_to_lower_ratio(upper, lower)
    domain_is_ip = is_domain_ip(domain)
    subdomains = count_subdomains(domain, domain_is_ip)
    url_entropy = shannon_entropy(url)
    domain_entropy = shannon_entropy(domain)
    path_entropy = shannon_entropy(path if path is not None else "")
    query_entropy = shannon_entropy(query if query is not None else "")
    fragment_entropy = shannon_entropy(fragment if fragment is not None else "")
    char_trans_entropy = character_transition_entropy(domain)
    digit_len_ratio = digit_to_length_ratio(digits, u_len)
    char_len_ratio = char_to_length_ratio(al_count, u_len)
    special_len_ratio = specialchar_to_length_ratio(special_chars, u_len)
    tld, mtld = check_tld_and_mtld(domain, tlds)
    features = {
        "dots": dots, # ok
        "at": at_symbols, # ok
        "equals": equals, # ok
        "slashes": slashes, # ok
        "hyphens": hyphens, # ok
        "colons": colons, # ok
        "question_marks": qm, # ok
        "digits": digits, # ok
        "and": ands, # ok
        "underscore": underscores, # ok
        "tilde": tildes, # ok
        "percent": percents, # ok
        "lowercase": lower, # ok
        "uppercase": upper, # ok
        "upper_to_lower_ratio": upper_lower_ratio, # ok
        "is_https": https_flag,# ok
        "url_length": u_len,# ok
        "domain_length": domain_len,# ok
        "path_length": path_len,# ok
        "path_depth": path_dep,# ok
        "query_length": query_len,# ok
        "query_count": query_count,# ok
        "fragment_length": fragment_len,# ok
        "se_url": url_entropy, # ok
        "se_domain": domain_entropy,# ok
        "se_path": path_entropy,# ok
        "se_query": query_entropy,# ok
        "se_fragment": fragment_entropy,# ok
        "cte_domain": char_trans_entropy, # ok
        "is_domain_ip": domain_is_ip,# ok
        "is_tld_iana_reg" : tld,# ok
        "is_mtld" : mtld,# ok
        "subdomains": subdomains, # ok
        "special_chars": special_chars,# ok
        "digit_to_length_ratio": digit_len_ratio, # ok
        "char_to_length_ratio": char_len_ratio,# ok
        "specialchar_to_length_ratio": special_len_ratio, # ok
        "url": url,
        "domain": domain,
        "path": path,
        "query": query,
        "fragment": fragment,
    }

    return features

def process_urls(urls: List[str],
                 max_workers: int = 8,
                 timeout: float = None) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(extract_features_for_url, u): u for u in urls}

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                feat = future.result(timeout=timeout)
                results.append(feat)
            except Exception as e:
                # collect error info but continue processing others
                errors.append({"url": url, "error": str(e)})
    
    # Save results and optionally errors into a JSON object
    output = {
        "features": results,
        "errors": errors
    }

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "features.json")

    # write to file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to write JSON to {file_path}: {e}")

    return results

if __name__ == "__main__":
    urls = [
        "https://wise.com/es/swift-codes/BACUSVSSXXX"
    ]
    feats = process_urls(urls, max_workers=4)
    print(f"Processed {len(feats)} URLs, saved to features.json")
