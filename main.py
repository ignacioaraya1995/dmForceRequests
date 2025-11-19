import os
import pandas as pd
from glob import glob
from datetime import datetime

# --- SCRIPT START ---
print("🚀 Starting the data consolidation and cleaning script...")

# Ask for the client's name at the beginning
client_name = input("Please enter the client's name: ").strip()

# Validate that the name is not empty to avoid errors in the filename
while not client_name:
    print("❌ The client's name cannot be empty.")
    client_name = input("Please enter the client's name: ").strip()

print(f"✅ Client selected: {client_name}")


# --- INITIAL SETUP ---
distress_columns = [
    "30-60-Days_Distress", "Absentee", "Bankruptcy_Distress", "Debt-Collection_Distress",
    "Divorce_Distress", "Downsizing_Distress", "Estate_Distress", "Eviction_Distress",
    "Failed_Listing_Distress", "highEquity", "Inter_Family_Distress", "Judgment_Distress",
    "Lien_City_County_Distress", "Lien_HOA_Distress", "Lien_Mechanical_Distress",
    "Lien_Other_Distress", "Lien_Utility_Distress", "Low_income_Distress",
    "PoorCondition_Distress", "Preforeclosure_Distress", "Probate_Distress",
    "Prop_Vacant_Flag", "Senior_Distress", "Tax_Delinquent_Distress", "Violation_Distress"
]
unique1_columns = ["MailingFullStreetAddress", "MailingZIP5"]
unique2_columns = ["SitusFullStreetAddress", "SitusZIP5"]
name_column = ["FIPS"]
key_variables = [
    "LotSizeSqFt", "LTV", "MailingCity", "MailingState", "MailingStreet", "Owner_Type",
    "Owner1FirstName", "Owner1LastName", "OwnerNAME1FULL", "PropertyID", "saleDate",
    "SumLivingAreaSqFt", "totalValue", "Use_Type", "YearBuilt", "SitusCity",
    "SitusState", "Bedrooms", 
    "IsListedFlag" # <-- NEW: Add the column here to preserve it
]
columns_to_keep = distress_columns + unique1_columns + unique2_columns + name_column + key_variables
percentage_to_retain = 0.7

if not 0 < percentage_to_retain <= 1:
    raise ValueError("The percentage to retain must be a number between 0 and 1.")

output_dir = os.path.join(os.getcwd(), "Output File")
os.makedirs(output_dir, exist_ok=True)

current_dir = os.getcwd()
folders_to_process = ['Files']
folders = [f for f in folders_to_process if os.path.isdir(os.path.join(current_dir, f))]

total_folders = len(folders)
print(f"\n🧐 Found {total_folders} folders to process: {', '.join(folders)}\n")

all_dfs = []

for idx, folder in enumerate(folders, 1):
    print(f"--- 📂 Processing Folder {idx}/{total_folders}: '{folder}' ---")
    folder_path = os.path.join(current_dir, folder)

    csv_files = glob(os.path.join(folder_path, '*.csv'))
    if not csv_files:
        print(f"⚠️ No CSV files found in '{folder}'. Skipping.\n")
        continue

    print(f"   -> Found {len(csv_files)} CSV file(s). Consolidating...")

    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(file, low_memory=False)
            dfs.append(df)
        except Exception as e:
            print(f"   -> ❌ Error reading '{os.path.basename(file)}': {e}")
    if not dfs:
        print(f"   -> ⚠️ Could not read any dataframes in '{folder}'. Skipping.\n")
        continue

    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"   -> ✅ Consolidated into a dataframe with {combined_df.shape[0]:,} rows.")

    existing_columns = [col for col in columns_to_keep if col in combined_df.columns]
    combined_df = combined_df[existing_columns]
    print(f"   -> ✅ Kept {len(existing_columns)} relevant columns.")

    columns_to_check = ["MailingFullStreetAddress", "MailingZIP5", "SitusFullStreetAddress", "SitusZIP5"]
    rows_before = len(combined_df)
    combined_df.dropna(subset=columns_to_check, how='any', inplace=True)
    rows_after = len(combined_df)
    print(f"   -> 🧹 Cleaning: Removed {rows_before - rows_after:,} rows with incomplete addresses.")
    
    distress_existing = [col for col in distress_columns if col in combined_df.columns]
    distress_df = combined_df[distress_existing].fillna(0)
    combined_df['DistressCounter'] = distress_df.apply(lambda row: row.astype(bool).sum(), axis=1)
    print("   -> 🔢 Calculated 'DistressCounter' column.")
    
    rows_before = len(combined_df)
    unique1_existing = [col for col in unique1_columns if col in combined_df.columns]
    if unique1_existing:
        combined_df.drop_duplicates(subset=unique1_existing, inplace=True)

    unique2_existing = [col for col in unique2_columns if col in combined_df.columns]
    if unique2_existing:
        combined_df.drop_duplicates(subset=unique2_existing, inplace=True)
    rows_after = len(combined_df)
    print(f"   -> 🧹 Cleaning: Removed {rows_before - rows_after:,} duplicate records.")

    combined_df.sort_values(by='DistressCounter', ascending=False, inplace=True)

    total_rows = combined_df.shape[0]
    cutoff_index = max(1, int(total_rows * percentage_to_retain))
    combined_df = combined_df.iloc[:cutoff_index]
    print(f"   -> 🎯 Kept the top {percentage_to_retain:.0%} ({len(combined_df):,} rows) by 'DistressCounter'.\n")

    all_dfs.append(combined_df)


# --- FINAL PROCESSING ---
print("--- ⚙️ Performing Final Processing on Consolidated Data ---")

final_df = pd.concat(all_dfs, ignore_index=True)
print(f"   -> ✅ Total consolidated records: {len(final_df):,} rows.")

# NEW: The order is modified to include the new column
new_column_order = [
    "FIPS", "PropertyID", "SitusFullStreetAddress", "SitusCity", "SitusState", "SitusZIP5",
    "MailingFullStreetAddress", "MailingCity", "MailingState", "MailingZIP5", "OwnerNAME1FULL",
    "Owner1FirstName", "Owner1LastName", "Owner_Type", "LotSizeSqFt", "LTV", "saleDate",
    "SumLivingAreaSqFt", "totalValue", "Use_Type", "YearBuilt", "Bedrooms", 
    "IsListedFlag", # <-- NEW: Position of the column
    "DistressCounter"
]

existing_distress_cols = [col for col in distress_columns if col in final_df.columns]
final_column_order = new_column_order + existing_distress_cols

# Ensure only columns that exist in the df are used
final_column_order_existing = [col for col in final_column_order if col in final_df.columns]
final_df = final_df[final_column_order_existing]
print(f"   -> ✅ Columns reordered, with {len(existing_distress_cols)} 'distress' columns added to the end.")

# NEW: Add the new name to the dictionary
rename_columns = {
    "SitusFullStreetAddress": "PROPERTY ADDRESS", "SitusCity": "PROPERTY CITY",
    "SitusState": "PROPERTY STATE", "SitusZIP5": "PROPERTY ZIP",
    "MailingFullStreetAddress": "MAILING ADDRESS", "MailingCity": "MAILING CITY",
    "MailingState": "MAILING STATE", "MailingZIP5": "MAILING ZIP",
    "OwnerNAME1FULL": "OWNER FULL NAME", "Owner1FirstName": "OWNER FIRST NAME",
    "Owner1LastName": "OWNER LAST NAME", "Owner_Type": "OWNER TYPE",
    "Use_Type": "PROPERTY TYPE",
    "IsListedFlag": "LISTED FLAG" # <-- NEW: Rename the column
}
final_df.rename(columns=rename_columns, inplace=True)
print("   -> ✅ Standardized column names.")

def capitalize_text(series):
    if pd.api.types.is_string_dtype(series):
        return series.str.title()
    return series

fips_file_path = os.path.join(current_dir, "FIPs.xlsx")
if os.path.exists(fips_file_path):
    try:
        fips_df = pd.read_excel(fips_file_path)
        if all(col in fips_df.columns for col in ['FIPS Code', 'County']):
            final_df = pd.merge(final_df, fips_df[['FIPS Code', 'County']], left_on='FIPS', right_on='FIPS Code', how='left')
            final_df.drop('FIPS Code', axis=1, inplace=True)
            final_df.rename(columns={'County': 'COUNTY'}, inplace=True)
            
            # Reorder to place COUNTY after PROPERTY STATE if it exists
            if 'PROPERTY STATE' in final_df.columns and 'COUNTY' in final_df.columns:
                cols = final_df.columns.tolist()
                prop_state_idx = cols.index('PROPERTY STATE')
                cols.insert(prop_state_idx + 1, cols.pop(cols.index('COUNTY')))
                final_df = final_df[cols]
            print("   -> ✅ 'COUNTY' column added from FIPs file.")
    except Exception as e:
        print(f"   -> ❌ Error processing FIPs.xlsx: {e}")

final_df.columns = final_df.columns.str.upper()

# --- INTERACTIVE FILTERS ---
print("\n--- 📝 Interactive Filters (Optional) ---\n")

def apply_filter(df, column_name, filter_type):
    initial_count = len(df)
    if initial_count == 0:
        print(f"No data to filter by {column_name}. Skipping.")
        return df

    if filter_type == 'text':
        unique_items = sorted(df[column_name].dropna().unique())
        print(f"Available values for '{column_name}': {', '.join(map(str, unique_items))}")
        desired_items_str = input(f"Enter desired '{column_name}' values (comma-separated), or press Enter to skip: ").strip().lower()
        if not desired_items_str:
            return df
        desired_list = [t.strip() for t in desired_items_str.split(',') if t.strip()]
        df = df[df[column_name].str.lower().isin(desired_list)]
    
    elif filter_type == 'numeric':
        current_min = df[column_name].min()
        current_max = df[column_name].max()
        print(f"Current range for '{column_name}': Min = {current_min:,.2f}, Max = {current_max:,.2f}")
        try:
            min_val_str = input("Enter the minimum value (or Enter to skip): ")
            max_val_str = input("Enter the maximum value (or Enter to skip): ")
            min_val = float(min_val_str) if min_val_str else current_min
            max_val = float(max_val_str) if max_val_str else current_max
            
            if min_val > max_val:
                min_val, max_val = max_val, min_val
                print("   -> ⚠️ Minimum is greater than maximum; values have been swapped.")
            
            df = df[(df[column_name] >= min_val) & (df[column_name] <= max_val)]
        except ValueError:
            print("   -> ❌ Error: Please enter valid numeric values. Filter not applied.")

    removed = initial_count - len(df)
    print(f"   -> Filter applied. Removed {removed:,} rows. {len(df):,} rows remaining.\n")
    return df

if input("Do you want to filter by OWNER TYPE? (yes/no): ").strip().lower() == 'yes':
    final_df = apply_filter(final_df, 'OWNER TYPE', 'text')

if input("Do you want to filter by PROPERTY TYPE? (yes/no): ").strip().lower() == 'yes':
    final_df = apply_filter(final_df, 'PROPERTY TYPE', 'text')
    
if input("Do you want to filter by TOTALVALUE? (yes/no): ").strip().lower() == 'yes':
    final_df = apply_filter(final_df, 'TOTALVALUE', 'numeric')


# --- FINAL CLEANUP ---
print("\n--- 🧹 Final Cleanup and Formatting ---")

if 'LTV' in final_df.columns:
    initial_count = len(final_df)
    ltv_str = final_df['LTV'].astype(str)
    mask = (
        ltv_str.str.lower().str.contains('unknown', na=False) | 
        (pd.to_numeric(final_df['LTV'], errors='coerce') <= 999)
    )
    final_df = final_df[mask | final_df['LTV'].isna()]
    removed = initial_count - len(final_df)
    print(f"   -> Removed {removed:,} rows with LTV > 999. {len(final_df):,} rows remaining.")
    final_df['LTV'] = pd.to_numeric(final_df['LTV'], errors='coerce')

text_cols = ['OWNER TYPE', 'PROPERTY TYPE', 'COUNTY']
for col in text_cols:
    if col in final_df.columns:
        final_df[col] = capitalize_text(final_df[col])
print("   -> Applied title case formatting to key text columns.")

# --- DUPLICATE REMOVAL FROM PREVIOUS FILES ---
print("\n--- 🗑️ Duplicate Removal (Optional) ---")
remove_duplicates = input("Do you want to remove properties listed in previous files (from 'Dupes' folder)? (yes/no): ").strip().lower()

if remove_duplicates == 'yes':
    dupes_folder = os.path.join(current_dir, "Dupes")
    if os.path.exists(dupes_folder):
        dupes_files = glob(os.path.join(dupes_folder, '*.csv')) + glob(os.path.join(dupes_folder, '*.xlsx'))
        
        if dupes_files:
            print(f"\n   -> Found {len(dupes_files)} file(s) in the 'Dupes' folder. Reading addresses...")
            dupes_addresses = set()
            
            for file in dupes_files:
                try:
                    df = pd.read_csv(file, low_memory=False) if file.endswith('.csv') else pd.read_excel(file)
                    
                    if 'PROPERTY ADDRESS' in df.columns:
                        valid_addresses = df['PROPERTY ADDRESS'].dropna().astype(str).str.strip().str.lower()
                        dupes_addresses.update(valid_addresses)
                    else:
                        print(f"      -> ⚠️ Warning: The file '{os.path.basename(file)}' does not contain a 'PROPERTY ADDRESS' column.")
                        
                except Exception as e:
                    print(f"      -> ❌ Error processing file '{os.path.basename(file)}': {e}")
            
            if dupes_addresses:
                print(f"   -> Read {len(dupes_addresses):,} unique addresses to use as a filter.")
                initial_count = len(final_df)
                
                consolidated_addresses = final_df['PROPERTY ADDRESS'].str.strip().str.lower()
                
                mask = ~consolidated_addresses.isin(dupes_addresses)
                
                final_df = final_df[mask]
                
                removed_count = initial_count - len(final_df)
                
                print("\n   --- Duplicate Filter Results ---")
                print(f"   ✅ Properties removed: {removed_count:,}")
                print(f"   ➡️ Properties remaining: {len(final_df):,}")
            else:
                print("\n   -> ⚠️ No valid addresses found in the 'Dupes' files to compare against.")
        else:
            print("\n   -> ⚠️ No CSV or XLSX files found in the 'Dupes' folder.")
    else:
        print("\n   -> ⚠️ 'Dupes' folder not found. Please ensure it exists in the same directory as the script.")


# --- SAVE AND FINAL SUMMARY ---

# Generate the filename dynamically
today_date_str = datetime.now().strftime('%m-%d-%Y')
file_name = f"{client_name} Consolidated {today_date_str}.xlsx"
output_file = os.path.join(output_dir, file_name)

# --- NEW LOGIC TO SAVE WITH FORMATTING ---
print(f"\n💾 Saving final file with formatting to: {output_file}")

# Create an ExcelWriter object using the XlsxWriter engine
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    # Write the DataFrame to the 'Consolidated' sheet without the default header
    final_df.to_excel(writer, sheet_name='Consolidated', index=False, header=False, startrow=1)

    # Get the xlsxwriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Consolidated']

    # Define the cell formats
    # Format 1: Black background, white font, bold
    header_format_main = workbook.add_format({
        'bold': True,
        'font_color': '#FFFFFF',
        'bg_color': '#000000',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })

    # Format 2: Yellow background, black font, bold
    header_format_distress = workbook.add_format({
        'bold': True,
        'font_color': '#000000',
        'bg_color': '#FFC000',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })

    # Create a set of the distress column headers for quick lookup
    distress_headers_set = {col.upper() for col in distress_columns}

    # Write the custom header with the defined formats
    for col_num, value in enumerate(final_df.columns.values):
        if value in distress_headers_set:
            worksheet.write(0, col_num, value, header_format_distress)
        else:
            worksheet.write(0, col_num, value, header_format_main)
        
        # Adjust column width for better readability
        column_len = max(len(str(value)), final_df[value].astype(str).str.len().max())
        worksheet.set_column(col_num, col_num, min(column_len + 2, 50)) # Set width, with a max of 50


# --- FINAL SUMMARY REPORT ---
print("\n" + "="*50)
print("📊 FINAL PROCESS SUMMARY".center(50))
print("="*50)

total_records = len(final_df)
print(f"📝 TOTAL FINAL RECORDS: {total_records:,}")
print("-" * 50)

if 'COUNTY' in final_df.columns and not final_df['COUNTY'].dropna().empty:
    counties_str = ', '.join(sorted(final_df['COUNTY'].dropna().unique()))
    print(f"🗺️ COUNTIES PRESENT: {counties_str}")
else:
    print("🗺️ COUNTY: Not available or no data")
print("-" * 50)

if 'PROPERTY TYPE' in final_df.columns and not final_df['PROPERTY TYPE'].dropna().empty:
    prop_types_str = ', '.join(sorted(final_df['PROPERTY TYPE'].dropna().unique()))
    print(f"🏠 PROPERTY TYPES: {prop_types_str}")
else:
    print("🏠 PROPERTY TYPE: Not available or no data")
print("-" * 50)

if 'OWNER TYPE' in final_df.columns and not final_df['OWNER TYPE'].dropna().empty:
    owner_types_str = ', '.join(sorted(final_df['OWNER TYPE'].dropna().unique()))
    print(f"👤 OWNER TYPES: {owner_types_str}")
else:
    print("👤 OWNER TYPE: Not available or no data")
print("-" * 50)

if 'TOTALVALUE' in final_df.columns and not final_df['TOTALVALUE'].dropna().empty:
    min_value = final_df['TOTALVALUE'].min()
    max_value = final_df['TOTALVALUE'].max()
    print(f"💰 TOTAL VALUE RANGE: ${min_value:,.2f} - ${max_value:,.2f}")
else:
    print("💰 TOTALVALUE: Not available or no data")
print("="*50)

print("\n🎉 Process completed successfully! 🎉")