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
    dataset_name = 'matches'
    if dataset_name not in dataset_ids:
        client.create_dataset(dataset_name)
        print("New dataset '" + dataset_name + "' created.")

    tables = client.list_tables("league-of-legends-analysis." + dataset_name)
    table_ids = list(map(lambda x: x.table_id, tables))
    table_name = "match-details-v2"
    if table_name not in table_ids:
        #filename = 'match_history.csv'
        table_id = "league-of-legends-analysis." + dataset_name + "." + table_name
        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.CSV
        #job_config.autodetect = True
        job_config.schema = [
            bigquery.SchemaField("gameId", "STRING"),
            bigquery.SchemaField("start_time", "FLOAT"),
            bigquery.SchemaField("duration", "INTEGER"),
            bigquery.SchemaField("queue", "INTEGER"),
            bigquery.SchemaField("win", "BOOLEAN"),
            bigquery.SchemaField("championName", "STRING"),
            bigquery.SchemaField("role", "STRING"),
            bigquery.SchemaField("lane", "STRING"),
            bigquery.SchemaField("position", "STRING"),
            bigquery.SchemaField("kills", "INTEGER"),
            bigquery.SchemaField("deaths", "INTEGER"),
            bigquery.SchemaField("assists", "INTEGER"),
            bigquery.SchemaField("damage_to_champs", "INTEGER"),
            bigquery.SchemaField("damage_to_obj", "INTEGER"),
            bigquery.SchemaField("damage_taken", "INTEGER"),
            bigquery.SchemaField("gold", "INTEGER"),
            bigquery.SchemaField("cs", "INTEGER"),
            bigquery.SchemaField("vision_score", "INTEGER"),
            bigquery.SchemaField("longest_life", "INTEGER"),
        ]
        job_config.skip_leading_rows = 1

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
    dataset_name = 'matches'
    if dataset_name not in dataset_ids:
        print("Dataset does not exist. Please run main")
    else:
        tables = client.list_tables("league-of-legends-analysis." + dataset_name)
        table_ids = list(map(lambda x: x.table_id, tables))
        table_name = "match-details-v2"
        if table_name not in table_ids:
            print("Table does not exist. Please run main")
        else:
            table_id = "league-of-legends-analysis." + dataset_name + "." + table_name
            job_config = bigquery.LoadJobConfig()
            job_config.source_format = bigquery.SourceFormat.CSV
            #job_config.autodetect = True
            job_config.schema = [
                bigquery.SchemaField("gameId", "STRING"),
                bigquery.SchemaField("start_time", "FLOAT"),
                bigquery.SchemaField("duration", "INTEGER"),
                bigquery.SchemaField("queue", "INTEGER"),
                bigquery.SchemaField("win", "BOOLEAN"),
                bigquery.SchemaField("championName", "STRING"),
                bigquery.SchemaField("role", "STRING"),
                bigquery.SchemaField("lane", "STRING"),
                bigquery.SchemaField("position", "STRING"),
                bigquery.SchemaField("kills", "INTEGER"),
                bigquery.SchemaField("deaths", "INTEGER"),
                bigquery.SchemaField("assists", "INTEGER"),
                bigquery.SchemaField("damage_to_champs", "INTEGER"),
                bigquery.SchemaField("damage_to_obj", "INTEGER"),
                bigquery.SchemaField("damage_taken", "INTEGER"),
                bigquery.SchemaField("gold", "INTEGER"),
                bigquery.SchemaField("cs", "INTEGER"),
                bigquery.SchemaField("vision_score", "INTEGER"),
                bigquery.SchemaField("longest_life", "INTEGER"),
            ]
            job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
            job_config.skip_leading_rows = 1

            # load the csv into bigquery
            with open(filename, "rb") as source_file:
                job = client.load_table_from_file(source_file, table_id, job_config=job_config)
            job.result()  # Waits for table load to complete.

            destination_table = client.get_table(table_id)  # Make an API request.
            print("Total {} rows.".format(destination_table.num_rows))

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

#create_match_table("match_history.csv")
#add_match_table("new_games.csv")