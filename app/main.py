import dotenv
import matplotlib.pyplot as plt
import seaborn as sns
from kagglehub.pandas_datasets import load_pandas_dataset

dotenv.load_dotenv()
import pandas as pd

owner_slug = "datasnaek"
dataset_slug = "youtube-new"
dataset_version = "115"
csv_file_name = "GBvideos.csv"
json_file_name = "GB_category_id.json"
dataset_handle = f"{owner_slug}/{dataset_slug}"

if __name__ == "__main__":
    gb_videos_df: pd.DataFrame = load_pandas_dataset(
        handle=dataset_handle,
        path=csv_file_name,
        sql_query=None,
    )

    gb_category_df: pd.DataFrame = load_pandas_dataset(
        handle=dataset_handle,
        path=json_file_name,
        sql_query=None,
    )

    mapping_between_category_id_and_name = {}

    for items in gb_category_df["items"]:
        category_id = int(items["id"])
        category_name = items["snippet"]["title"]
        mapping_between_category_id_and_name[category_id] = category_name

    gb_videos_df["engagement_score"] = (
        gb_videos_df["likes"]
        + gb_videos_df["dislikes"]
        + (gb_videos_df["comment_count"] * 5)
    )
    gb_videos_df["engagement_per_view"] = (
        gb_videos_df["engagement_score"] / gb_videos_df["views"]
    )
    gb_videos_df["category_name"] = gb_videos_df["category_id"].map(
        mapping_between_category_id_and_name
    )
    gb_videos_df["category_name"] = gb_videos_df["category_name"].fillna(
        gb_videos_df["category_id"].astype(str)
    )

    plt.figure(figsize=(15, 8))
    sns.barplot(
        data=gb_videos_df, x="category_name", y="engagement_per_view", estimator="mean"
    )
    plt.title("Engagement score per View by Category")
    plt.xlabel("Category")
    plt.ylabel("Engagement Score per View")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("engagement_per_view_by_category_name.png")
