const fs = require("fs");

const scaler = JSON.parse(fs.readFileSync("scaler.json", "utf8"));

function loadCSV(file) {
  const text = fs.readFileSync(file, "utf8").trim();
  return text.split("\n").map(row => row.split(",").map(Number));
}
const eigvecs = loadCSV("eigvecs_95.csv");

const X_new = [
  {
    dots: 2,
    equals: 4,
    slashes: 5,
    hyphens: 5,
    colons: 1,
    question_marks: 1,
    digits: 23,
    and: 3,
    underscore: 5,
    tilde: 0,
    percent: 8,
    lowercase: 168,
    uppercase: 0,
    upper_to_lower_ratio: 0,
    is_https: 0,
    url_length: 231,
    domain_length: 17,
    path_length: 53,
    path_depth: 3,
    query_length: 153,
    query_count: 4,
    fragment_length: 0,
    se_url: 4.86,
    se_domain: 3.45,
    se_path: 4.25,
    se_query: 4.61,
    cte_domain: 3.75,
    subdomains: 1,
    special_chars: 6,
    digit_to_length_ratio: 0.1,
    char_to_length_ratio: 0.73,
    specialchar_to_length_ratio: 0.03,
  }
];

const featureNames = Object.keys(X_new[0]);
const values = featureNames.map(f => X_new[0][f]);

const scaled = values.map((x, i) => (x - scaler.mean[i]) / scaler.scale[i]);

function dotVectorMatrix(vec, mat) {
  const out = [];
  for (let j = 0; j < mat[0].length; j++) {
    let sum = 0;
    for (let i = 0; i < vec.length; i++) {
      sum += vec[i] * mat[i][j];
    }
    out.push(sum);
  }
  return out;
}

const X_new_pca = dotVectorMatrix(scaled, eigvecs);

X_new_pca.forEach((val, i) => {
  console.log(`PC${i+1}: ${val}`);
});
