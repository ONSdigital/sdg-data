# SDG Data Repository

[![Build Status](https://travis-ci.org/MangoTheCat/sdg-data.svg?branch=develop)](https://travis-ci.org/MangoTheCat/sdg-data)
 [![LICENSE.](https://img.shields.io/badge/license-OGL--3-brightgreen.svg?style=flat)](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

This repository holds the UK data for SDG reporting. The data is served via a static http server.

# Servers

The develop branch serves from the `gh-pages` branch on this repository. This is for staging.

The master branch serves from the main deployment org and is for prod.

# Routes:

Loosely speaking with have: `<datatype>/<format>/<id>.ext` and support csv and json file formats.

## Data

The main data set, the raw data lives in `data/` in the repo.

```
data/<format>/<id>.<ext>

data/csv/1-2-1.csv
data/json/1-2-1.json
```

e.g. https://mangothecat.github.io/data/json/1-2-1.json

### Edges

```
edges/csv/1-2-1.csv
edges/json/1-2-1.csv
```

### Combined data and edges

```
comb/csv/1-2-1.csv
comb/json/1-2-1.csv
```

## Metadata

```
meta/json/<id>.json
```


## Build time routes

### Headline data

```
headline/<format>/<id>.<ext>
headline/json/all.json
```

### Everything

The following is metadata and headlines for all indicators in one blob for the build.

```
meta/json/all.json
```

Scripts:

`build_data.py`: Builds main data, headline, and edges output in csv, and json.

Packages:

The `scripts/sdg` folder holds the supporting python package for `build_data.py`.

## License

Data is under [open government license v3](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). 
