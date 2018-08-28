# SDG Data Repository

This repository holds the [Rwanda data](https://sustainabledevelopment-rwanda.github.io/sdg-indicators) for SDG reporting. The data is served via a static http server.

# Servers

The develop branch serves from the `gh-pages` branch on this repository. This is for staging.

The master branch serves from the main deployment org and is for prod.

# Routes:

Loosely speaking with have: `/<datatype>/<id>.<format>` and support csv and json file formats. You can also look at the file structure at https://github.com/sustainabledevelopment-rwanda/sdg-data/tree/gh-pages and it shows how it's all laid out.

## Versions

We're planning for versioned APIs. Right now the root location is the latest API. Other versions will be available. For example the development branch of the API code will be available by adding `dev` to the beginning of the path. e.g. `/dev/<datatype>/<id>.<format>`.

## Data

The main data set, the raw data lives in `/data/` in the repo.

```
/data/<id>.<format>

/data/1-2-1.csv
/data/1-2-1.json
```

e.g. https://sustainabledevelopment-rwanda.github.io/sdg-data/data/1-2-1.json

### Edges

```
/edges/1-2-1.csv
/edges/1-2-1.json
```

### Combined data and edges

```
/comb/1-2-1.csv
/comb/1-2-1.json
```

## Metadata

```
/meta/<id>.json
```


## Build time routes

At build time you'll need everything. Rather than making you download each indicator separately we have an ID of `all` which you can use.

### Headline data

Headlines json comes formatted as records, instead of in list format.

```
/headline/<id>.<format>
/headline/all.json
```

### Metadata

The following is all metadata for all indicators in one blob for the build.

```
/meta/all.json
```

It's a JSON object with `{<id>: <meta>}` pairs.

Scripts:

* `check_data.py`: Runs data and metadata checks and will prevent deployment if fails.
* `build_data.py`: Builds main data, headline, and edges output in csv, and json.

Packages:

This uses the `sdg` package from the `sdg-build` repository during the build.
