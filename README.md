# OpenAIRE Affiliation Harvesting

A small Python tool for extracting author affiliation information from publication pages. It reads publication URLs from TSV files, fetches the HTML pages, applies publisher specific extraction rules, and writes the extracted affiliations to a CSV file.

The project was built for controlled batches of scholarly publication records, especially records that need affiliation metadata for OpenAIRE style enrichment.

## What it does

- Reads input records with `publisher`, `id`, and `url` fields.
- Fetches each publication page with browser like request headers.
- Detects the publisher domain from the final response URL.
- Extracts affiliations using XPath rules, regex rules, or custom parser functions.
- Applies simple per publisher delays to avoid sending requests too quickly.
- Writes extracted affiliations and notes to `files/output.csv`.

## Repository structure

| Path | Purpose |
| --- | --- |
| `main.py` | Main script for loading input files, fetching URLs, extracting affiliations, and writing results. |
| `profiles.yaml` | Publisher extraction profiles. Each profile defines domains, publisher names, delays, XPath rules, regex rules, and optional UDFs. |
| `scraping.py` | Core extraction logic for applying XPath and regex rules. |
| `udfs.py` | Custom extraction functions for publishers whose data needs special parsing. |
| `utils.py` | Helpers for loading profiles, fetching pages, parsing HTML, and writing CSV output. |
| `timed_object.py` | Simple delay utility used for per publisher request throttling. |
| `nlp_services.py` | Optional spaCy based NER utilities. These are included but not used by the default run. |
| `files/to_test.tsv` | Example input file. |
| `files/output.csv` | Example output file. |
| `requirements.txt` | Python dependencies. |

## Input format

Input files must be TSV files with these columns:

```tsv
publisher	id	url
Institute of Electrical and Electronics Engineers (IEEE)	doi_________::example	https://ieeexplore.ieee.org/document/example
```

By default, `main.py` reads:

```python
files = ['files/to_test.tsv']
```

To process other files, edit this list in `main.py`.

## Setup

Use Python 3.11 if possible.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment with:

```bash
.venv\Scripts\activate
```

## Run

```bash
python main.py
```

The script currently shuffles the input records and processes the first 5 rows:

```python
filtered_df = filtered_df.sample(frac=1, random_state=12345).reset_index(drop=True)
filtered_df = filtered_df.head(5)
```

Remove or change `head(5)` if you want to process more records.

## Output

Results are written to:

```text
files/output.csv
```

The output columns are:

| Column | Description |
| --- | --- |
| `publisher` | Publisher name from the input file. |
| `id` | Record identifier from the input file. |
| `url` | Original URL from the input file. |
| `affiliations` | Extracted affiliations as a list. |
| `note` | Status message, error message, or extraction note. |

If `files/output.csv` already exists, new rows are appended.

## Publisher profiles

Publisher extraction rules are configured in `profiles.yaml`.

A profile can use XPath:

```yaml
link.springer.com:
  xpath: "//meta[@name='citation_author_institution']/@content"
  publisher:
    - "Springer Science and Business Media LLC"
  delay_string: "springer"
  delay:
    from: 3
    to: 7
```

A profile can also use regex with a custom UDF:

```yaml
ieeexplore.ieee.org:
  regex: "xplGlobal.document.metadata=(\\{.*?\\});"
  udf: "ieee"
  publisher:
    - "IEEE"
    - "Institute of Electrical and Electronics Engineers (IEEE)"
  delay_string: "ieee"
  delay:
    from: 3
    to: 7
```

To add a new publisher:

1. Add a new domain entry in `profiles.yaml`.
2. Add an XPath rule if the affiliations are directly available in the HTML.
3. Add a regex rule and a UDF in `udfs.py` if the affiliations are embedded inside JSON or another custom format.
4. Make sure the publisher name in the input file matches one of the profile publisher names.

## Notes

- Some publishers are excluded inside `main.py` using the `excluded_publishers` list.
- The script marks a domain as blocked if it receives a `403` response, except for Wiley pages.
- PDF URLs are skipped because the default extractor works on HTML pages.
- The current implementation is intended for batch extraction, not continuous crawling.
