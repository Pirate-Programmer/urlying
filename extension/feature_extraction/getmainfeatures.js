function extractFeatures(url) {
  let u;
  try {
    u = new URL(url);
  } catch (e) {
    throw new Error("Invalid URL");
  }

  const domain = u.hostname;
  const path = u.pathname;
  const query = u.search.replace(/^\?/, ""); // remove leading ?
  const fragment = u.hash.replace(/^#/, ""); // remove leading #

  const countChars = (str, regex) => (str.match(regex) || []).length;

  const features = {
    dots: countChars(url, /\./g),
    equals: countChars(url, /=/g),
    slashes: countChars(url, /\//g),
    hyphens: countChars(url, /-/g),
    colons: countChars(url, /:/g),
    question_marks: countChars(url, /\?/g),
    digits: countChars(url, /\d/g),
    and: countChars(url, /&/g),
    underscore: countChars(url, /_/g),
    tilde: countChars(url, /~/g),
    percent: countChars(url, /%/g),
    lowercase: countChars(url, /[a-z]/g),
    uppercase: countChars(url, /[A-Z]/g),
    upper_to_lower_ratio: (countChars(url, /[A-Z]/g)) / (countChars(url, /[a-z]/g) + 1e-5),
    is_https: u.protocol === "https:" ? 1 : 0,
    url_length: url.length,
    domain_length: domain.length,
    path_length: path.length,
    path_depth: countChars(path, /\//g),
    query_length: query.length,
    query_count: query.length > 0 ? countChars(query, /&/g) + 1 : 0,
    fragment_length: fragment.length,
    se_url: countChars(url, /[a-z]/g),       // lowercase letters in full URL
    se_domain: countChars(domain, /[a-z]/g),
    se_path: countChars(path, /[a-z]/g),
    se_query: countChars(query, /[a-z]/g),
    cte_domain: countChars(domain, /[a-z]/g), // same as se_domain here
    subdomains: domain.split(".").length - 2 > 0 ? domain.split(".").length - 2 : 0,
    special_chars: countChars(url, /[^a-zA-Z0-9]/g),
    digit_to_length_ratio: countChars(url, /\d/g) / (url.length + 1e-5),
    char_to_length_ratio: countChars(url, /[a-zA-Z]/g) / (url.length + 1e-5),
    specialchar_to_length_ratio: countChars(url, /[^a-zA-Z0-9]/g) / (url.length + 1e-5),
  };

  return features;
}


// Example usage
const url = "https://example.com/test/path123?param=456&x=abc#frag";
console.log(extractFeatures(url));
