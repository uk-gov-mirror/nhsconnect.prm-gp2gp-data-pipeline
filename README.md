# prm-gp2gp-data-pipeline

This repo contains the data pipeline responsible for deriving GP2GP metrics from data sources such as NMS.

## Running

### Extracting Spine data from NMS

Run the following query for the desired time range and save the results as a csv.

```
index="spine2-live" service="gp2gp"
| search interactionID="urn:nhs:names:services:gp2gp/*"
| fields _time, conversationID, GUID, interactionID, fromNACS, toNACS, messageRef, jdiEvent
| fields - _raw
```

## Developing

Common development workflows are defined in the `tasks` script.

These generally work by running a command in a virtual environment configured via `tox.ini`.

### Prerequisites

- Python 3
- [Tox](https://tox.readthedocs.io/en/latest/#)
- [Minio](https://github.com/minio/minio)

### Running the unit and integration tests

`./tasks test`

### Running the end to end tests

`./tasks e2e-test`

### Running tests, linting, and type checking

`./tasks validate`

### Auto Formatting

`./tasks format`

### Dependency Scanning

`./tasks check-deps`

### ODS Portal Pipeline
This pipeline will fetch ODS codes and names of all active GP practices and save to json file.

To run the ODS Portal pipeline first create virtual dev environment:

`./tasks devenv`

Then run the pipeline command:

`ods-portal-pipeline --output-file "<output-file>.json"`

### Dashboard Pipeline

This pipeline will derive GP2GP metrics and metadata for practices produced by the ODS Portal Pipeline. It does this by performing a number of transformations on GP2GP messages provided by NMS.
 
The following examples show how to run this pipeline.

Example 1 - Outputting to file
 
`gp2gp-dashboard-pipeline --month 6 --year 2019 --practice-list-file "data/practice-list.json" --input-files "data/jun.csv.gz,data/july.csv.gz" --practice-metrics-output-file "data/jun-practice-metrics.json" --practice-metadata-output-file "data/jun-practice-metadata.json"`

Example 2 - Outputting to S3

`gp2gp-dashboard-pipeline --month 6 --year 2019 --practice-list-file "data/practice-list.json" --input-files "data/jun.csv.gz,data/july.csv.gz" --output-bucket "example-bucket" --practice-metrics-output-key "jun-practice-metrics.json" --practice-metadata-output-key "jun-practice-metadata.json"`
