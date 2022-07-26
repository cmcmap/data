CMCmap Data
==========

## How to submit a change via Pull Request

1. Log in to Github
1. Open the file you want to change, for example [settlements.civmap.json](https://github.com/cmcmap/data/tree/master/settlements.civmap.json)
1. On the top right, click the edit pen
1. Make your changes
1. Check for JSON formatting errors: paste everything into [JSONLint](https://jsonlint.com/?reformat=no)
1. At the bottom, click `Propose file change`
1. Once the page loads, click `Create Pull Request`

Thank you for contributing to CMCmap!

---

## Maintenance

### Generating settlements JSON from spreadsheet

Download the spreadsheet in Tab-separated Values format (`.tsv`) and run this command:

```bash
cat "CivClassic Settlements - Settlements (1).tsv" | python3 scripts/overlay_from_tsv.py 'omit=founded=major=active=Activity Index - Jan. 2018=Activity Index - Feb. 2018=Activity Index - Apr. 2018=Activity Index - May 2018=Appomattox Builder\'s Association - Rating' | sed -E 's/\}, \{/\},\n    \{/g' > settlements.civmap.json
```

The `omit=...` argument removes these spreadsheet columns from the output.

The `sed -E 's/\}, \{/\},\n    \{/g'` splits the file into many lines, to make viewing diffs easier.
