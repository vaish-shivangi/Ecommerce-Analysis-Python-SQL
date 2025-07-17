import pandas as pd
import pymysql
import os

# List of CSV files and their corresponding table names
csv_files = [
    ('customers.csv', 'customers'),
    ('orders.csv', 'orders'),
    ('sellers.csv', 'sellers'),
    ('products.csv', 'products'),
    ('geolocation.csv', 'geolocation'),
    ('payments.csv', 'payments'),
    ('order_items.csv', 'order_items')
]

# Folder path where your CSV files are stored
folder_path = r"E:\project\Ecommerce EDA+SQL\dataset"
 
# Connect to the MySQL database using pymysql
try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='1234',
        database='ecommerce'
    )
    cursor = conn.cursor()
    print("✅ Connected to MySQL database successfully.")
except Exception as e:
    print(f"❌ Error connecting to MySQL: {e}")
    exit()

# Function to map pandas dtypes to SQL types
def get_sql_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return 'INT'
    elif pd.api.types.is_float_dtype(dtype):
        return 'FLOAT'
    elif pd.api.types.is_bool_dtype(dtype):
        return 'BOOLEAN'
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return 'DATETIME'
    else:
        return 'TEXT'

# Loop through all CSV files
for csv_file, table_name in csv_files:
    file_path = os.path.join(folder_path, csv_file)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        continue

    print(f"📄 Processing {csv_file}...")

    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Clean column names
    df.columns = [col.replace(' ', '_').replace('-', '_').replace('.', '_') for col in df.columns]

    # Replace NaN with None (NULL in SQL)
    df = df.where(pd.notnull(df), None)

    # Create table if it doesn't exist
    columns = ', '.join([f'`{col}` {get_sql_type(df[col].dtype)}' for col in df.columns])
    create_table_query = f'CREATE TABLE IF NOT EXISTS `{table_name}` ({columns})'
    try:
        cursor.execute(create_table_query)
    except Exception as e:
        print(f"❌ Failed to create table `{table_name}`: {e}")
        continue

    # Insert data row by row
    for _, row in df.iterrows():
        values = tuple(None if pd.isna(x) else x for x in row)
        placeholders = ', '.join(['%s'] * len(row))
        columns_str = ', '.join([f'`{col}`' for col in df.columns])
        insert_query = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"
        try:
            cursor.execute(insert_query, values)
        except Exception as e:
            print(f"❌ Failed to insert row into `{table_name}`: {e}")
            continue

    conn.commit()
    print(f"✅ Inserted data into `{table_name}`.\n")

# Close connection
cursor.close()
conn.close()
print("🔒 MySQL connection closed.")
