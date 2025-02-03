# Using Kedro with Celery for Your Data Processing Use Case


1. Orchestrating complex workflows (via Kedro Pipelines).
2. Parallelizing tasks (via Celery Workers).
3. Ensuring fault tolerance (Celery handles task retries).
4. Tracking versions of data transformations (Kedro’s versioned datasets).

## 1️⃣ How Kedro + Celery Can Work in Your Case
### Workflow Overview
#### Kedro:
Defines the data pipeline for reading JSON from APIs, processing in Pandas, converting to CSV, zipping it, and uploading to S3.
Ensures data versioning and modular pipeline execution.

#### Celery:
Orchestrates pipeline execution.
Parallelizes independent steps (e.g., API calls, CSV generation, and PPT creation).
Retries failed tasks automatically.

## 2️⃣ Step-by-Step Implementation
### Step 1: Install Required Dependencies
```
pip install kedro kedro-viz celery boto3 pandas
```

### Step 2: Define Kedro Pipeline for Data Processing
Modify src/my_kedro_project/pipelines/data_processing/nodes.py:
```
import pandas as pd
import requests
import zipfile
import os
import boto3
from io import BytesIO

def fetch_api_data(api_url: str) -> pd.DataFrame:
    """Fetch JSON data from API and return as Pandas DataFrame"""
    response = requests.get(api_url)
    response.raise_for_status()
    return pd.DataFrame(response.json())

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process data: Convert to uppercase and format for CSV"""
    df["name"] = df["name"].str.upper()
    return df

def save_csv_and_zip(df: pd.DataFrame, output_path: str) -> str:
    """Save processed DataFrame as CSV, then zip it"""
    csv_path = output_path + "/data.csv"
    zip_path = output_path + "/data.zip"

    df.to_csv(csv_path, index=False)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(csv_path, os.path.basename(csv_path))
    
    return zip_path

def upload_to_s3(zip_file: str, bucket_name: str, s3_path: str):
    """Upload zipped CSV file to S3"""
    s3 = boto3.client("s3")
    s3.upload_file(zip_file, bucket_name, s3_path)
    return f"Uploaded {zip_file} to {s3_path}"
```

###  Step 3: Define Kedro Pipeline
Modify src/my_kedro_project/pipelines/data_processing/pipeline.py:

```
from kedro.pipeline import Pipeline, node
from .nodes import fetch_api_data, process_data, save_csv_and_zip, upload_to_s3

def create_pipeline(**kwargs):
    return Pipeline([
        node(fetch_api_data, inputs="params:api_url", outputs="raw_data"),
        node(process_data, inputs="raw_data", outputs="processed_data"),
        node(save_csv_and_zip, inputs=["processed_data", "params:output_path"], outputs="zip_file"),
        node(upload_to_s3, inputs=["zip_file", "params:s3_bucket", "params:s3_path"], outputs="upload_status")
    ])
```

✅ Now, the pipeline fetches data from an API, processes it, converts it to CSV, zips it, and uploads to S3.

### Step 4: Configure Kedro Catalog for Data Versioning
Modify conf/base/catalog.yml:
```
raw_data:
  type: pandas.CSVDataSet
  filepath: data/raw/raw_data.csv
  versioned: true

processed_data:
  type: pandas.CSVDataSet
  filepath: data/processed/processed_data.csv
  versioned: true
```  
✅ Each dataset is automatically versioned.

### Step 5: Run Kedro Pipeline in Celery
Modify src/my_kedro_project/celery_tasks.py:
```
from celery import Celery
from kedro.framework.session import KedroSession

app = Celery("tasks", broker="pyamqp://guest@localhost//")

@app.task
def run_kedro_pipeline():
    """Run the Kedro pipeline asynchronously via Celery"""
    with KedroSession.create("my_kedro_project") as session:
        session.run()
    return "Pipeline Execution Complete"
```    
✅ Now, you can trigger Kedro pipelines as Celery tasks!

### Step 6: Running the Pipeline with Celery
Start the Celery worker:
```
celery -A celery_tasks worker --loglevel=info
```
Trigger the workflow:
```
from celery_tasks import run_kedro_pipeline
run_kedro_pipeline.delay()
```
✅ This ensures that Kedro’s pipeline runs asynchronously using Celery workers!

### Step 7: Generating PPT and Uploading to S3
Modify src/my_kedro_project/pipelines/data_processing/nodes.py:
```
from pptx import Presentation
from io import BytesIO

def create_ppt(data: pd.DataFrame, template_path: str) -> str:
    """Generate a PowerPoint presentation based on template"""
    prs = Presentation(template_path)
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    title = slide.shapes.title
    title.text = f"Report for {data.iloc[0]['name']}"

    ppt_path = "/tmp/report.pptx"
    prs.save(ppt_path)
    return ppt_path

def upload_ppt_to_s3(ppt_path: str, bucket_name: str, s3_path: str):
    """Upload PPT file to S3"""
    s3 = boto3.client("s3")
    s3.upload_file(ppt_path, bucket_name, s3_path)
    return f"Uploaded {ppt_path} to {s3_path}"
```

Modify pipeline.py:

```
from .nodes import create_ppt, upload_ppt_to_s3

def create_pipeline(**kwargs):
    return Pipeline([
        node(fetch_api_data, inputs="params:api_url", outputs="raw_data"),
        node(process_data, inputs="raw_data", outputs="processed_data"),
        node(save_csv_and_zip, inputs=["processed_data", "params:output_path"], outputs="zip_file"),
        node(upload_to_s3, inputs=["zip_file", "params:s3_bucket", "params:s3_path"], outputs="upload_status"),
        node(create_ppt, inputs=["processed_data", "params:ppt_template"], outputs="ppt_file"),
        node(upload_ppt_to_s3, inputs=["ppt_file", "params:s3_bucket", "params:ppt_s3_path"], outputs="ppt_upload_status")
    ])
```    
✅ Now, the pipeline also generates and uploads a PowerPoint report!

### Step 8: Deploy Kedro Viz
kedro-viz-deployment.yaml:
```commandline
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kedro-viz
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kedro-viz
  template:
    metadata:
      labels:
        app: kedro-viz
    spec:
      containers:
      - name: kedro-viz
        image: myrepo/kedro-viz:latest
        command: ["kedro", "viz"]
        ports:
        - containerPort: 4141
---
apiVersion: v1
kind: Service
metadata:
  name: kedro-viz-service
spec:
  selector:
    app: kedro-viz
  ports:
    - protocol: TCP
      port: 4141
      targetPort: 4141

```

```commandline
kubectl apply -f kedro-viz-deployment.yaml
```