import os
import pandas as pd
from glob import glob

# Definir las columnas basadas en las categorías proporcionadas
distress_columns = [
    "30-60-Days_Distress",
    "Absentee",
    "Bankruptcy_Distress",
    "Debt-Collection_Distress",
    "Divorce_Distress",
    "Downsizing_Distress",
    "Estate_Distress",
    "Eviction_Distress",
    "Failed_Listing_Distress",
    "highEquity",
    "Inter_Family_Distress",
    "Judgment_Distress",
    "Lien_City_County_Distress",
    "Lien_HOA_Distress",
    "Lien_Mechanical_Distress",
    "Lien_Other_Distress",
    "Lien_Utility_Distress",
    "Low_income_Distress",
    "PoorCondition_Distress",
    "Preforeclosure_Distress",
    "Probate_Distress",
    "Prop_Vacant_Flag",
    "Senior_Distress",
    "Tax_Delinquent_Distress",
    "Violation_Distress"
]

unique1_columns = ["MailingFullStreetAddress", "MailingZIP5"]
unique2_columns = ["SitusFullStreetAddress", "SitusZIP5"]
name_column = ["FIPS"]
key_variables = [
    "LotSizeSqFt",
    "LTV",
    "MailingCity",
    "MailingState",
    "MailingStreet",
    "Owner_Type",
    "Owner1FirstName",
    "Owner1LastName",
    "OwnerNAME1FULL",
    "PropertyID",
    "saleDate",
    "SumLivingAreaSqFt",
    "totalValue",
    "Use_Type",
    "YearBuilt",
    "SitusCity",
    "SitusState",
    "Bedrooms",
    #"ConcurrentMtg1LoanType",
    "IsListedFlag"     
    #"PrevSalesPrice" 
]

columns_to_keep = distress_columns + unique1_columns + unique2_columns + name_column + key_variables
percentage_to_retain = 0.7

if not 0 < percentage_to_retain <= 1:
    raise ValueError("El porcentaje a retener debe ser un número entre 0 y 1.")

output_dir = os.path.join(os.getcwd(), "Output File")
os.makedirs(output_dir, exist_ok=True)

current_dir = os.getcwd()
folders_to_process = ['Files']
folders = [f for f in folders_to_process if os.path.isdir(os.path.join(current_dir, f))]

total_folders = len(folders)
print(f"Se encontraron {total_folders} carpetas para procesar.\n")

# Lista para almacenar todos los DataFrames consolidados
all_dfs = []

for idx, folder in enumerate(folders, 1):
    print(f"Procesando carpeta {idx}/{total_folders}: '{folder}'")
    folder_path = os.path.join(current_dir, folder)

    csv_files = glob(os.path.join(folder_path, '*.csv'))
    if not csv_files:
        print(f"No se encontraron archivos CSV en '{folder}'. Saltando.\n")
        continue

    print(f"  Se encontraron {len(csv_files)} archivo(s) CSV en '{folder}'. Leyendo y consolidando...")

    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(file, low_memory=False)
            dfs.append(df)
        except Exception as e:
            print(f"    Error al leer '{file}': {e}")
    if not dfs:
        print(f"  No se pudieron leer dataframes en '{folder}'. Saltando.\n")
        continue

    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"  Consolidado {len(dfs)} archivo(s) en un dataframe con {combined_df.shape[0]} filas.")

    existing_columns = [col for col in columns_to_keep if col in combined_df.columns]
    combined_df = combined_df[existing_columns]
    print(f"  Se retuvieron {len(existing_columns)} columnas según lo especificado.")

    # Eliminar filas con celdas vacías en las columnas especificadas
    columns_to_check = ["MailingFullStreetAddress", "MailingZIP5", "SitusFullStreetAddress", "SitusZIP5"]
    combined_df.dropna(subset=columns_to_check, how='any', inplace=True)
    print(f"  Se eliminaron filas con celdas vacías en las columnas: {columns_to_check}.")

    distress_existing = [col for col in distress_columns if col in combined_df.columns]
    distress_df = combined_df[distress_existing].fillna(0)

    distress_counter = distress_df.apply(lambda row: row.astype(bool).sum(), axis=1)
    combined_df['DistressCounter'] = distress_counter
    print("  Se creó la variable 'DistressCounter'.")

    unique1_existing = [col for col in unique1_columns if col in combined_df.columns]
    if unique1_existing:
        combined_df.drop_duplicates(subset=unique1_existing, inplace=True)

    unique2_existing = [col for col in unique2_columns if col in combined_df.columns]
    if unique2_existing:
        combined_df.drop_duplicates(subset=unique2_existing, inplace=True)

    combined_df.sort_values(by='DistressCounter', ascending=False, inplace=True)

    total_rows = combined_df.shape[0]
    cutoff_index = max(1, int(total_rows * percentage_to_retain))
    combined_df = combined_df.iloc[:cutoff_index]

    all_dfs.append(combined_df)

# Combinar todos los DataFrames
final_df = pd.concat(all_dfs, ignore_index=True)

# Definir el nuevo orden de las columnas
new_column_order = [
    "FIPS",
    "PropertyID",
    "SitusFullStreetAddress",
    "SitusCity",
    "SitusState",
    "SitusZIP5",
    "MailingFullStreetAddress",
    "MailingCity",
    "MailingState",
    "MailingZIP5",
    "OwnerNAME1FULL",
    "Owner1FirstName",
    "Owner1LastName",
    "Owner_Type",
    "LotSizeSqFt",
    "LTV",
    "saleDate",
    "SumLivingAreaSqFt",
    "totalValue",
    "Use_Type",
    "YearBuilt",
    "Bedrooms",
    "DistressCounter",
    #"ConcurrentMtg1LoanType",     //Enable if the client needs to add the LoanType
    "IsListedFlag"     # //Enable is the client needs properties on market 
    #"PrevSalesPrice"    #//Enable is client needs last sale history
]

final_df = final_df[new_column_order]

# Renombrar las columnas
rename_columns = {
    "SitusFullStreetAddress": "PROPERTY ADDRESS",
    "SitusCity": "PROPERTY CITY",
    "SitusState": "PROPERTY STATE",
    "SitusZIP5": "PROPERTY ZIP",
    "MailingFullStreetAddress": "MAILING ADDRESS",
    "MailingCity": "MAILING CITY",
    "MailingState": "MAILING STATE",
    "MailingZIP5": "MAILING ZIP",
    "OwnerNAME1FULL": "OWNER FULL NAME",
    "Owner1FirstName": "OWNER FIRST NAME",
    "Owner1LastName": "OWNER LAST NAME",
    "Owner_Type": "OWNER TYPE",
    "Use_Type": "PROPERTY TYPE"
}

final_df.rename(columns=rename_columns, inplace=True)

# Función para capitalizar texto
def capitalize_text(series):
    if pd.api.types.is_string_dtype(series):
        return series.str.title()
    return series

# Procesar FIPS County
fips_file_path = os.path.join(current_dir, "FIPs.xlsx")
if os.path.exists(fips_file_path):
    try:
        fips_df = pd.read_excel(fips_file_path)
        if all(col in fips_df.columns for col in ['FIPS Code', 'County']):
            final_df = pd.merge(
                final_df,
                fips_df[['FIPS Code', 'County']],
                left_on='FIPS',
                right_on='FIPS Code',
                how='left'
            )
            final_df.drop('FIPS Code', axis=1, inplace=True)
            final_df.rename(columns={'County': 'COUNTY'}, inplace=True)
            
            cols = final_df.columns.tolist()
            prop_state_idx = cols.index('PROPERTY STATE')
            cols.insert(prop_state_idx + 1, cols.pop(cols.index('COUNTY')))
            final_df = final_df[cols]
            
            print("  Se agregó la columna COUNTY basada en los códigos FIPS.")
    except Exception as e:
        print(f"  Error al procesar FIPs.xlsx: {e}")

# Convertir headers a mayúsculas
final_df.columns = final_df.columns.str.upper()

# Filtro interactivo para OWNER TYPE
filter_owner = input("\n¿Desea filtrar por OWNER TYPE? (si/no): ").strip().lower()
if filter_owner == 'si':
    unique_owners = final_df['OWNER TYPE'].dropna().unique()
    print("\nOWNER TYPE disponibles:", ', '.join(map(str, unique_owners)))
    
    desired_owners = input("Ingrese los OWNER TYPE deseados (separados por coma): ").strip().lower()
    desired_list = [t.strip() for t in desired_owners.split(',') if t.strip()]
    
    if desired_list:
        initial_count = len(final_df)
        final_df = final_df[final_df['OWNER TYPE'].str.lower().isin(desired_list)]
        removed = initial_count - len(final_df)
        print(f"\nSe eliminaron {removed} filas. Quedan {len(final_df)} filas.")

# Filtro interactivo para PROPERTY TYPE
filter_property = input("\n¿Desea filtrar por PROPERTY TYPE? (si/no): ").strip().lower()
if filter_property == 'si':
    unique_props = final_df['PROPERTY TYPE'].dropna().unique()
    print("\nPROPERTY TYPE disponibles:", ', '.join(map(str, unique_props)))
    
    desired_props = input("Ingrese los PROPERTY TYPE deseados (separados por coma): ").strip().lower()
    desired_list = [t.strip() for t in desired_props.split(',') if t.strip()]
    
    if desired_list:
        initial_count = len(final_df)
        final_df = final_df[final_df['PROPERTY TYPE'].str.lower().isin(desired_list)]
        removed = initial_count - len(final_df)
        print(f"\nSe eliminaron {removed} filas. Quedan {len(final_df)} filas.")

# Filtro interactivo para TOTALVALUE
filter_value = input("\n¿Desea filtrar por TOTALVALUE? (si/no): ").strip().lower()
if filter_value == 'si':
    current_min = final_df['TOTALVALUE'].min()
    current_max = final_df['TOTALVALUE'].max()
    print(f"\nRango actual: Mínimo = {current_min}, Máximo = {current_max}")
    
    try:
        min_val = float(input("Ingrese el valor mínimo: "))
        max_val = float(input("Ingrese el valor máximo: "))
        
        if min_val > max_val:
            print("\n¡Advertencia! El mínimo es mayor que el máximo. Se intercambiarán.")
            min_val, max_val = max_val, min_val
        
        initial_count = len(final_df)
        final_df = final_df[(final_df['TOTALVALUE'] >= min_val) & (final_df['TOTALVALUE'] <= max_val)]
        removed = initial_count - len(final_df)
        
        print(f"\nSe eliminaron {removed} filas. Quedan {len(final_df)} filas.")
        print(f"Nuevo rango: Mínimo = {final_df['TOTALVALUE'].min()}, Máximo = {final_df['TOTALVALUE'].max()}")
    except ValueError:
        print("\nError: Ingrese valores numéricos válidos.")

# Filtro para LTV
if 'LTV' in final_df.columns:
    initial_count = len(final_df)
    ltv_str = final_df['LTV'].astype(str)
    mask = (
        ltv_str.str.lower().str.contains('unknown', na=False) | 
        (pd.to_numeric(final_df['LTV'], errors='coerce') <= 999)
    )
    final_df = final_df[mask | final_df['LTV'].isna()]
    removed = initial_count - len(final_df)
    print(f"\nSe eliminaron {removed} filas con LTV > 999. Quedan {len(final_df)} filas.")
    final_df['LTV'] = pd.to_numeric(final_df['LTV'], errors='coerce')

# Aplicar formato de texto
text_cols = ['OWNER TYPE', 'PROPERTY TYPE', 'COUNTY']
for col in text_cols:
    if col in final_df.columns:
        final_df[col] = capitalize_text(final_df[col])

# Guardar archivo final
output_file = os.path.join(output_dir, "Consolidated Files.xlsx")
final_df.to_excel(output_file, index=False)
print(f"\nArchivo guardado en: {output_file}")
print("Procesamiento completado.")

# [Todo el código anterior permanece igual hasta antes del análisis final]

# Consultar sobre eliminación de duplicados de archivos previos
remove_duplicates = input("\n¿Desea eliminar propiedades listadas en archivos previos (Dupes)? (si/no): ").strip().lower()

if remove_duplicates == 'si':
    dupes_folder = os.path.join(current_dir, "Dupes")
    if os.path.exists(dupes_folder):
        # Leer todos los archivos en la carpeta Dupes
        dupes_files = glob(os.path.join(dupes_folder, '*.csv')) + glob(os.path.join(dupes_folder, '*.xlsx'))
        
        if dupes_files:
            print(f"\nLeyendo {len(dupes_files)} archivos en la carpeta Dupes...")
            dupes_addresses = set()
            
            for file in dupes_files:
                try:
                    if file.endswith('.csv'):
                        df = pd.read_csv(file)
                    else:  # .xlsx
                        df = pd.read_excel(file)
                    
                    if 'PROPERTY ADDRESS' in df.columns:
                        dupes_addresses.update(df['PROPERTY ADDRESS'].dropna().astype(str).str.strip().str.lower())
                    
                except Exception as e:
                    print(f"  Error al procesar {os.path.basename(file)}: {e}")
            
            if dupes_addresses:
                initial_count = len(final_df)
                # Crear máscara para mantener solo propiedades NO encontradas en dupes
                mask = ~final_df['PROPERTY ADDRESS'].str.strip().str.lower().isin(dupes_addresses)
                final_df = final_df[mask]
                removed_count = initial_count - len(final_df)
                
                print(f"\nSe eliminaron {removed_count} propiedades que estaban listadas en archivos previos.")
                print(f"Quedan {len(final_df)} propiedades después de este filtro.")
            else:
                print("\nNo se encontraron direcciones en los archivos Dupes para comparar.")
        else:
            print("\nNo se encontraron archivos en la carpeta Dupes.")
    else:
        print("\nNo se encontró la carpeta Dupes.")





# Análisis final de los datos
print("\n****RESULTS****\n")

# 1. Total de registros
total_records = len(final_df)
print(f"TOTAL DE REGISTROS: {total_records:,}")
print("-" * 40)

# 2. County analysis
if 'COUNTY' in final_df.columns:
    counties = final_df['COUNTY'].dropna().unique()
    counties_str = ', '.join(sorted([str(c) for c in counties if pd.notna(c)]))
    print(f"COUNTY: {counties_str}")
else:
    print("COUNTY: No disponible")
print("-" * 40)

# 3. Property Type analysis
if 'PROPERTY TYPE' in final_df.columns:
    prop_types = final_df['PROPERTY TYPE'].dropna().unique()
    prop_types_str = ', '.join(sorted([str(p) for p in prop_types if pd.notna(p)]))
    print(f"PROPERTY TYPE: {prop_types_str}")
else:
    print("PROPERTY TYPE: No disponible")
print("-" * 40)

# 4. Owner Type analysis
if 'OWNER TYPE' in final_df.columns:
    owner_types = final_df['OWNER TYPE'].dropna().unique()
    owner_types_str = ', '.join(sorted([str(o) for o in owner_types if pd.notna(o)]))
    print(f"OWNER TYPE: {owner_types_str}")
else:
    print("OWNER TYPE: No disponible")
print("-" * 40)

# 5. TotalValue range
if 'TOTALVALUE' in final_df.columns:
    min_value = final_df['TOTALVALUE'].min()
    max_value = final_df['TOTALVALUE'].max()
    print(f"TOTALVALUE RANGE: Min {min_value:,.2f} - Max {max_value:,.2f}")
else:
    print("TOTALVALUE: No disponible")
print("-" * 40)

print("\nProcesamiento completado.")