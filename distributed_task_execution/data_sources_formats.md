# Requirement
Read the data from various input sources and write to different output sources. 
The Input sources can be json from API calls, Queries reading data from postgres and content from S3 as CSV files.
The output sources can be again API calls sending back json data, insert queries to Postgres and Upload to S3 as CSV.

Please note that 
1. the data will be finally in pandas dataframe in the memory
2. the sources can be API call, Postgres DB or S3
3. the data format can be JSON or CSV

Can you recommend any existing open source enterprise level python frameworks (if there any) which allow the components to be plugged and plugged out in different combinations and handle the data?

If there are no such frameworks, please provide your answers in terms of design patterns (both object oriented and functional) to be used to solve this problem.

## Versioning and Visualization in Kedro
Kedro is a data engineering framework that provides:

Versioned datasets (so transformations are traceable).
Visualized workflows using Kedro-Viz.

### 1: Install Kedro
```
pip install kedro
kedro new my_kedro_project
cd my_kedro_project
```


### 2: Define a Pipeline with Versioning
Kedro automatically version-controls datasets in conf/base/catalog.yml.
#### Define a Data Catalog with Versioning
```commandline
raw_users:
  type: pandas.CSVDataSet
  filepath: data/raw/users.csv
  versioned: true

processed_users:
  type: pandas.CSVDataSet
  filepath: data/processed/users.csv
  versioned: true

```

✅ Now, any updates to users.csv will be versioned.

✅ You can revert to old versions using Kedro’s Data Catalog API.


### 3: Define the Processing Logic
Modify src/my_kedro_project/pipelines/data_engineering/nodes.py
```
import pandas as pd

def process_users(raw_users: pd.DataFrame) -> pd.DataFrame:
    raw_users["name"] = raw_users["name"].str.upper()
    return raw_users
```

### 4: Define the Pipeline
Modify src/my_kedro_project/pipelines/data_engineering/pipeline.py:
```
from kedro.pipeline import Pipeline, node
from .nodes import process_users

def create_pipeline(**kwargs):
    return Pipeline([
        node(process_users, inputs="raw_users", outputs="processed_users"),
    ])
```

### 5: Visualize the Pipeline
```
pip install kedro-viz
kedro viz
```

