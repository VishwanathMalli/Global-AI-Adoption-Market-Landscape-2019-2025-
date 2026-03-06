
import os
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


# CONFIG — CHANGE THESE 2 VALUES ONLY

DB_PASSWORD = "Your sql password"   # your MySQL password
BASE_PATH   = r"file path"         #your raw inputs file path

DB_USER = "root"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "ai_adoption_db"


# STEP 1 — CONNECT TO MYSQL & CREATE DATABASE

print("=" * 60)
print("STEP 1: Connecting to MySQL ...")

engine_server = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}"
)
with engine_server.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS ai_adoption_db"))
    print("  Database 'ai_adoption_db' ready.")

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
print("  MySQL engine ready.")


# STEP 2 — LOAD ALL 6 RAW CSV FILES

print("\nSTEP 2: Loading raw CSV files ...")

df_mck   = pd.read_csv(f"{BASE_PATH}/mckinsey_ai_survey.csv")
df_stan  = pd.read_csv(f"{BASE_PATH}/stanford_ai_index.csv")
df_stat  = pd.read_csv(f"{BASE_PATH}/statista_ai_market.csv")
df_oecd  = pd.read_csv(f"{BASE_PATH}/oecd_ai_policy.csv")
df_idc   = pd.read_csv(f"{BASE_PATH}/idc_ai_spending.csv")
df_cloud = pd.read_csv(f"{BASE_PATH}/cloud_provider_revenue.csv")

print(f"  McKinsey  : {df_mck.shape[0]} rows, {df_mck.shape[1]} cols")
print(f"  Stanford  : {df_stan.shape[0]} rows, {df_stan.shape[1]} cols")
print(f"  Statista  : {df_stat.shape[0]} rows, {df_stat.shape[1]} cols")
print(f"  OECD      : {df_oecd.shape[0]} rows, {df_oecd.shape[1]} cols")
print(f"  IDC       : {df_idc.shape[0]} rows, {df_idc.shape[1]} cols")
print(f"  Cloud     : {df_cloud.shape[0]} rows, {df_cloud.shape[1]} cols")


# STEP 3 — CLEAN COLUMN NAMES & REMOVE DUPLICATES

print("\nSTEP 3: Cleaning column names ...")

def clean_columns(df):
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    return df

df_mck   = clean_columns(df_mck).drop_duplicates()
df_stan  = clean_columns(df_stan).drop_duplicates()
df_stat  = clean_columns(df_stat).drop_duplicates()
df_oecd  = clean_columns(df_oecd).drop_duplicates()
df_idc   = clean_columns(df_idc).drop_duplicates()
df_cloud = clean_columns(df_cloud).drop_duplicates()

print("  Done — all column names standardised, duplicates removed.")


# STEP 4 — CLEAN EACH DATASET

print("\nSTEP 4: Cleaning each dataset ...")

country_map = {
    "USA": "United States", "US":  "United States", "U.S.": "United States",
    "UK":  "United Kingdom", "UAE": "United Arab Emirates",
}

# ── McKinsey ──────────────────────────────────────────────────────────────────
df_mck["ai_adoption_rate_pct"] = pd.to_numeric(df_mck["ai_adoption_rate_pct"], errors="coerce")
df_mck["sample_size"]          = pd.to_numeric(df_mck["sample_size"],          errors="coerce")
df_mck["year"]                 = df_mck["year"].astype(int)

df_mck["ai_adoption_rate_pct"] = df_mck["ai_adoption_rate_pct"].fillna(df_mck["ai_adoption_rate_pct"].median())
df_mck["sample_size"]          = df_mck["sample_size"].fillna(df_mck["sample_size"].median())
df_mck["industry"]             = df_mck["industry"].fillna("Unknown").str.strip().str.title()
df_mck["ai_function"]          = df_mck["ai_function"].fillna("Not Specified").str.strip().str.title()
df_mck["region"]               = df_mck["region"].fillna("Unknown").str.strip().str.title()

df_mck = df_mck.sort_values(["industry", "region", "year"]).reset_index(drop=True)
df_mck["yoy_growth_pct"] = (
    df_mck.groupby(["industry", "region"])["ai_adoption_rate_pct"]
    .pct_change() * 100
).round(2)

print(f"  McKinsey  cleaned : {df_mck.shape[0]} rows, {df_mck.shape[1]} cols")

# ── Stanford ──────────────────────────────────────────────────────────────────
df_stan = df_stan.drop_duplicates(subset=["country", "year"])
df_stan["year"] = df_stan["year"].astype(int)

for col in ["ai_investment_usd_bn", "patents_filed", "research_papers",
            "notable_ml_models", "ai_startups_funded"]:
    df_stan[col] = pd.to_numeric(df_stan[col], errors="coerce")
    df_stan[col] = df_stan[col].fillna(df_stan[col].median())

df_stan["country"]      = df_stan["country"].str.strip().replace(country_map)
df_stan["country_code"] = df_stan["country_code"].str.strip().str.upper()
df_stan["region"]       = df_stan["region"].str.strip().str.title()

print(f"  Stanford  cleaned : {df_stan.shape[0]} rows, {df_stan.shape[1]} cols")

# ── Statista ──────────────────────────────────────────────────────────────────
df_stat = df_stat.drop_duplicates(subset=["country", "year"])
df_stat["year"]                  = df_stat["year"].astype(int)
df_stat["market_revenue_usd_bn"] = pd.to_numeric(df_stat["market_revenue_usd_bn"], errors="coerce")
df_stat["growth_rate_yoy_pct"]   = pd.to_numeric(df_stat["growth_rate_yoy_pct"],   errors="coerce")
df_stat["cagr_5yr_pct"]          = pd.to_numeric(df_stat["cagr_5yr_pct"],          errors="coerce")
df_stat["market_revenue_usd_bn"] = df_stat["market_revenue_usd_bn"].fillna(df_stat["market_revenue_usd_bn"].median())
df_stat["country"]               = df_stat["country"].str.strip().replace(country_map)
df_stat["region"]                = df_stat["region"].str.strip().str.title()

print(f"  Statista  cleaned : {df_stat.shape[0]} rows, {df_stat.shape[1]} cols")

# ── OECD ──────────────────────────────────────────────────────────────────────
df_oecd = df_oecd.drop_duplicates(subset=["country", "year"])
df_oecd["year"]               = df_oecd["year"].astype(int)
df_oecd["ai_readiness_score"] = pd.to_numeric(df_oecd["ai_readiness_score"], errors="coerce")
df_oecd["policy_count"]       = pd.to_numeric(df_oecd["policy_count"],       errors="coerce")
df_oecd["ai_talent_score"]    = pd.to_numeric(df_oecd["ai_talent_score"],    errors="coerce")
df_oecd["is_g20_member"]      = pd.to_numeric(df_oecd["is_g20_member"],      errors="coerce")
df_oecd["ai_readiness_score"] = df_oecd["ai_readiness_score"].fillna(df_oecd["ai_readiness_score"].median())
df_oecd["policy_count"]       = df_oecd["policy_count"].fillna(0)
df_oecd["country"]            = df_oecd["country"].str.strip().replace(country_map)
df_oecd["income_group"]       = df_oecd["income_group"].str.strip().str.title()

# Drop these columns from OECD — Stanford already has them
# This prevents pandas creating region_x/region_y and country_code_x/country_code_y on merge
df_oecd = df_oecd.drop(columns=["country_code", "region"], errors="ignore")

print(f"  OECD      cleaned : {df_oecd.shape[0]} rows, {df_oecd.shape[1]} cols")

# ── IDC ───────────────────────────────────────────────────────────────────────
df_idc["year"]                   = df_idc["year"].astype(int)
df_idc["ai_spending_usd_bn"]     = pd.to_numeric(df_idc["ai_spending_usd_bn"],     errors="coerce")
df_idc["pilot_to_prod_rate_pct"] = pd.to_numeric(df_idc["pilot_to_prod_rate_pct"], errors="coerce")
df_idc["ai_spending_usd_bn"]     = df_idc["ai_spending_usd_bn"].fillna(df_idc["ai_spending_usd_bn"].median())
df_idc["pilot_to_prod_rate_pct"] = df_idc["pilot_to_prod_rate_pct"].fillna(df_idc["pilot_to_prod_rate_pct"].median())
df_idc["barrier_type"]           = df_idc["barrier_type"].fillna("Unknown")
df_idc["industry"]               = df_idc["industry"].str.strip().str.title()

# Drop region from IDC — McKinsey already has it
# This prevents pandas creating region_x/region_y on merge
df_idc = df_idc.drop(columns=["region"], errors="ignore")

print(f"  IDC       cleaned : {df_idc.shape[0]} rows, {df_idc.shape[1]} cols")

# ── Cloud ─────────────────────────────────────────────────────────────────────
df_cloud["year"]                 = df_cloud["year"].astype(int)
df_cloud["cloud_revenue_usd_bn"] = pd.to_numeric(df_cloud["cloud_revenue_usd_bn"], errors="coerce")
df_cloud["market_share_pct"]     = pd.to_numeric(df_cloud["market_share_pct"],     errors="coerce")
df_cloud["yoy_growth_pct"]       = pd.to_numeric(df_cloud["yoy_growth_pct"],       errors="coerce")
df_cloud["provider_name"]        = df_cloud["provider_name"].str.strip()

print(f"  Cloud     cleaned : {df_cloud.shape[0]} rows, {df_cloud.shape[1]} cols")


# STEP 5 — EDA (Exploratory Data Analysis)

print("\nSTEP 5: EDA ...")

print("\n  --- Adoption Rate Summary Stats ---")
print(df_mck["ai_adoption_rate_pct"].describe().round(2))

print("\n  --- Average Adoption by Industry ---")
print(
    df_mck.groupby("industry")["ai_adoption_rate_pct"]
    .mean().round(2).sort_values(ascending=False)
)

print("\n  --- Global Adoption Trend by Year ---")
print(
    df_mck.groupby("year")["ai_adoption_rate_pct"]
    .agg(["mean", "min", "max"]).round(2)
)

print("\n  --- Top 5 Countries by Total AI Investment ---")
print(
    df_stan.groupby("country")["ai_investment_usd_bn"]
    .sum().round(2).sort_values(ascending=False).head(5)
)

print("\n  --- Cloud Market Share (Latest Year) ---")
latest = df_cloud["year"].max()
print(
    df_cloud[df_cloud["year"] == latest]
    [["provider_name", "cloud_revenue_usd_bn", "market_share_pct"]]
    .sort_values("market_share_pct", ascending=False)
    .to_string(index=False)
)

print("\n  --- Avg Pilot-to-Production Rate by Industry ---")
print(
    df_idc.groupby("industry")["pilot_to_prod_rate_pct"]
    .mean().round(1).sort_values(ascending=False)
)

print("\n  --- Top Scaling Barriers ---")
print(df_idc["barrier_type"].value_counts())

print("\n  --- Use Case Distribution ---")
print(df_idc["use_case_category"].value_counts())

print("\n  --- Outlier Detection: Adoption Rate (IQR method) ---")
Q1  = df_mck["ai_adoption_rate_pct"].quantile(0.25)
Q3  = df_mck["ai_adoption_rate_pct"].quantile(0.75)
IQR = Q3 - Q1
outliers = df_mck[
    (df_mck["ai_adoption_rate_pct"] < Q1 - 1.5 * IQR) |
    (df_mck["ai_adoption_rate_pct"] > Q3 + 1.5 * IQR)
]
print(f"  Outliers found: {len(outliers)}")
if len(outliers) > 0:
    print(outliers[["year", "industry", "region", "ai_adoption_rate_pct"]])


# STEP 6 — MERGE INTO 3 FINAL DATAFRAMES

print("\nSTEP 6: Merging into 3 final DataFrames ...")

# DataFrame 1: Industry data  (McKinsey + IDC)
# Joining on year + industry — no duplicate columns because we dropped region from IDC above
df_industry = pd.merge(
    df_mck,
    df_idc,
    on=["year", "industry"],
    how="left"
)

# DataFrame 2: Country/Geo data  (Stanford + OECD + Statista)
# No duplicate columns because we dropped country_code + region from OECD above
df_geo = pd.merge(
    df_stan,
    df_oecd,
    on=["country", "year"],
    how="left"
)
df_geo = pd.merge(
    df_geo,
    df_stat[["country", "year", "market_revenue_usd_bn", "growth_rate_yoy_pct", "cagr_5yr_pct"]],
    on=["country", "year"],
    how="left"
)

# DataFrame 3: Cloud provider data  (no merge needed — already standalone)
df_ai_cloud = df_cloud.copy()

print(f"  df_industry : {df_industry.shape[0]} rows, {df_industry.shape[1]} cols")
print(f"  Columns     : {df_industry.columns.tolist()}")
print(f"\n  df_geo      : {df_geo.shape[0]} rows, {df_geo.shape[1]} cols")
print(f"  Columns     : {df_geo.columns.tolist()}")
print(f"\n  df_ai_cloud : {df_ai_cloud.shape[0]} rows, {df_ai_cloud.shape[1]} cols")
print(f"  Columns     : {df_ai_cloud.columns.tolist()}")

# Confirm zero duplicate-suffix columns
dup_check = [c for c in df_industry.columns.tolist() + df_geo.columns.tolist()
             if c.endswith("_x") or c.endswith("_y")]
print(f"\n  Duplicate _x/_y columns: {dup_check if dup_check else 'NONE — clean!'}")

print("\n  Missing values in df_industry:")
mv = df_industry.isnull().sum()
print(mv[mv > 0] if mv[mv > 0].any() else "  None")

print("\n  Missing values in df_geo:")
mv2 = df_geo.isnull().sum()
print(mv2[mv2 > 0] if mv2[mv2 > 0].any() else "  None")


# STEP 7 — EXPORT CLEAN CSVs  (import these into Power BI)

print("\nSTEP 7: Exporting clean CSVs ...")

CLEAN_PATH = f"{BASE_PATH}/clean"
os.makedirs(CLEAN_PATH, exist_ok=True)

df_industry.to_csv(f"{CLEAN_PATH}/ai_industry_clean.csv", index=False)
df_geo.to_csv(     f"{CLEAN_PATH}/ai_geo_clean.csv",      index=False)
df_ai_cloud.to_csv(f"{CLEAN_PATH}/ai_cloud_clean.csv",    index=False)

print(f"  Saved to: {CLEAN_PATH}")
print("  ai_industry_clean.csv  ✓")
print("  ai_geo_clean.csv       ✓")
print("  ai_cloud_clean.csv     ✓")


# STEP 8 — UPLOAD TO MYSQL via SQLAlchemy
#   to_sql() auto-creates the table + maps all column types automatically
#   if_exists="replace"  →  drops and recreates on every run — no duplicates

print("\nSTEP 8: Uploading to MySQL ...")

df_industry.to_sql("ai_industry", con=engine, if_exists="replace", index=False, chunksize=500)
print(f"  Table 'ai_industry' → {len(df_industry)} rows loaded  ✓")

df_geo.to_sql("ai_geo", con=engine, if_exists="replace", index=False, chunksize=500)
print(f"  Table 'ai_geo'      → {len(df_geo)} rows loaded  ✓")

df_ai_cloud.to_sql("ai_cloud", con=engine, if_exists="replace", index=False, chunksize=500)
print(f"  Table 'ai_cloud'    → {len(df_ai_cloud)} rows loaded  ✓")


# STEP 9 — VERIFY: read back row counts from MySQL

print("\nSTEP 9: Verifying from MySQL ...")

with engine.connect() as conn:
    for table in ["ai_industry", "ai_geo", "ai_cloud"]:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"  {table:<15} : {count} rows in MySQL  ✓")

print("\n" + "=" * 60)
print("  PIPELINE COMPLETE!")
print(f"  Database : {DB_NAME}")
print("  Tables   : ai_industry  |  ai_geo  |  ai_cloud")
print("=" * 60)
print("\nNext:")
print("  MySQL Workbench  →  USE ai_adoption_db;  →  run the 20 SQL queries")
print(f"  Power BI         →  Get Data → Text/CSV → import 3 files from {CLEAN_PATH}")