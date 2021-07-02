# get data from Riot API
# save to csv
# upload to bigquery (1st time)
# get more data, save to csv, append to bigquery
# load data into dataframe for analysis, sort, filter etc. here
# https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-csv
# https://www.kaggle.com/rtatman/uploading-csv-to-bigquery/comments
from google.cloud import bigquery

def create_match_table(filename):
    project_id = 'league-of-legends-analysis'
    client = bigquery.Client(project=project_id)
    datasets = list(client.list_datasets()) 
    dataset_ids = list(map(lambda x: x.dataset_id, datasets))
    dataset_name = 'testdata'
    if dataset_name not in dataset_ids:
        client.create_dataset(dataset_name)
        print("New dataset '" + dataset_name + "' created.")

    tables = client.list_tables("league-of-legends-analysis." + dataset_name)
    table_ids = list(map(lambda x: x.table_id, tables))
    table_name = "test-table-3"
    if table_name not in table_ids:
        #filename = 'match_history.csv'
        table_id = "league-of-legends-analysis." + dataset_name + "." + table_name
        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.CSV
        job_config.autodetect = True

        # load the csv into bigquery
        with open(filename, "rb") as source_file:
            job = client.load_table_from_file(source_file, table_id, job_config=job_config)

        job.result()  # Waits for table load to complete.

        destination_table = client.get_table(table_id)  # Make an API request.
        print("Loaded {} rows.".format(destination_table.num_rows))
    else:
        print("Table already exists!")

def add_match_table(filename):
    project_id = 'league-of-legends-analysis'
    client = bigquery.Client(project=project_id)
    datasets = list(client.list_datasets()) 
    dataset_ids = list(map(lambda x: x.dataset_id, datasets))
    dataset_name = 'testdata'
    if dataset_name not in dataset_ids:
        print("Dataset does not exist. Please run main")
    else:
        tables = client.list_tables("league-of-legends-analysis." + dataset_name)
        table_ids = list(map(lambda x: x.table_id, tables))
        table_name = "test-table-3"
        if table_name not in table_ids:
            print("Table does not exist. Please run main")
        else:
            table_id = "league-of-legends-analysis." + dataset_name + "." + table_name
            job_config = bigquery.LoadJobConfig()
            job_config.source_format = bigquery.SourceFormat.CSV
            job_config.autodetect = True
            job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

            # load the csv into bigquery
            with open(filename, "rb") as source_file:
                job = client.load_table_from_file(source_file, table_id, job_config=job_config)
            job.result()  # Waits for table load to complete.

            destination_table = client.get_table(table_id)  # Make an API request.
            print("Loaded {} rows.".format(destination_table.num_rows))

def test():
    # Construct a BigQuery client object.
    project_id = 'league-of-legends-analysis'
    client = bigquery.Client(project=project_id)

    datasets = list(client.list_datasets()) 
    dataset_ids = list(map(lambda x: x.dataset_id, datasets))
    if "testdataset" not in dataset_ids:
        client.create_dataset("testdataset")

    tables = client.list_tables("league-of-legends-analysis.testdataset")
    table_ids = list(map(lambda x: x.table_id, tables))

    # create new table vs. append data
    if 'test-table-2' not in table_ids:
        filename = 'match_history.csv'
        table_id = "league-of-legends-analysis.testdataset.test-table-2"
        # job_config = bigquery.LoadJobConfig(
        #     schema=[
        #         bigquery.SchemaField("name", "STRING"),
        #         bigquery.SchemaField("post_abbr", "STRING"),
        #     ],
        #     skip_leading_rows=1,
        #     # The source format defaults to CSV, so the line below is optional.
        #     source_format=bigquery.SourceFormat.CSV,
        # )
        # uri = "gs://cloud-samples-data/bigquery/us-states/us-states.csv"

        # load_job = client.load_table_from_uri(
        #     uri, table_id, job_config=job_config
        # )  # Make an API request.

        # load_job.result()  # Waits for the job to complete.

        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.CSV
        job_config.autodetect = True

        # load the csv into bigquery
        with open(filename, "rb") as source_file:
            job = client.load_table_from_file(source_file, table_id, job_config=job_config)

        job.result()  # Waits for table load to complete.

        destination_table = client.get_table(table_id)  # Make an API request.
        print("Loaded {} rows.".format(destination_table.num_rows))
    else:
        filename = 'match_history.csv'
        table_id = "league-of-legends-analysis.testdataset.test-table-2"
        # job_config = bigquery.LoadJobConfig(
        #     write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        #     source_format=bigquery.SourceFormat.CSV,
        #     skip_leading_rows=1,
        # )

        # uri = "gs://cloud-samples-data/bigquery/us-states/us-states.csv"
        # load_job = client.load_table_from_uri(
        #     uri, table_id, job_config=job_config
        # )  # Make an API request.

        # load_job.result()  # Waits for the job to complete.

        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.CSV
        job_config.autodetect = True
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

        # load the csv into bigquery
        with open(filename, "rb") as source_file:
            job = client.load_table_from_file(source_file, table_id, job_config=job_config)

        job.result()  # Waits for table load to complete.

        destination_table = client.get_table(table_id)  # Make an API request.
        print("Loaded {} rows.".format(destination_table.num_rows))