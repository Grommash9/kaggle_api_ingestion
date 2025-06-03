# This is a very basic prompt file to get you started, feel free to amend as you please, though please use the dataset and file names provided

base_url = "https://www.kaggle.com/api/v1"
owner_slug = "datasnaek"
dataset_slug = "youtube-new"
dataset_version = "115"
csv_file_name = "GBvideos.csv"
json_file_name = "GB_category_id.json"

url = f"{base_url}/datasets/download/{owner_slug}/{dataset_slug}?datasetVersionNumber={dataset_version}"

import kagglehub

kagglehub.login()

