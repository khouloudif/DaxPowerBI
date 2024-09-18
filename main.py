import pandas as pd
import random
from faker import Faker
import os

# Initialize Faker
fake = Faker()

# Generate the Date Dimension
def generate_date_dimension(start_year=2023, num_days=365):
    date_dimension = []
    for i in range(num_days):
        date = pd.Timestamp(f'{start_year}-01-01') + pd.Timedelta(days=i)
        date_dimension.append({
            'DateKey': i + 1,
            'Date': date,
            'DayOfWeek': date.day_name(),
            'Month': date.month,
            'Quarter': (date.month - 1) // 3 + 1,
            'Year': date.year
        })
    return pd.DataFrame(date_dimension)

# Generate the Product Dimension
def generate_product_dimension(num_products=50):
    product_dimension = []
    for i in range(num_products):
        product_dimension.append({
            'ProductKey': i + 1,
            'ProductName': fake.unique.word().capitalize(),
            'Category': random.choice(['Electronics', 'Clothing', 'Furniture', 'Food']),
            'UnitPrice': round(random.uniform(5.0, 500.0), 2),
            'Supplier': fake.company()
        })
    return pd.DataFrame(product_dimension)

# Generate the Warehouse Dimension
def generate_warehouse_dimension(num_warehouses=10):
    warehouse_dimension = []
    for i in range(num_warehouses):
        warehouse_dimension.append({
            'WarehouseKey': i + 1,
            'WarehouseName': fake.company(),
            'Location': fake.city(),
            'TotalSquareFootage': random.randint(1000, 10000),
            'ManagerName': fake.name()
        })
    return pd.DataFrame(warehouse_dimension)

# Generate the Vendor Dimension
def generate_vendor_dimension(num_vendors=50):
    vendor_dimension = []
    for i in range(num_vendors):
        vendor_dimension.append({
            'VendorKey': i + 1,
            'VendorName': fake.company(),
            'Country': fake.country(),
            'ContactPerson': fake.name()
        })
    return pd.DataFrame(vendor_dimension)

# Generate the Date Bridge Table for each date type in fact table
def generate_date_bridge(fact_table, date_column):
    bridge_table = fact_table[[date_column]].drop_duplicates().reset_index(drop=True)
    bridge_table['DateKey'] = bridge_table.index + 1
    return bridge_table

# Function to generate lagged dates based on the received date
def generate_lagged_dates(date_received):
    # Create random time lags for different steps in the process
    lag_inspection = pd.Timedelta(days=random.randint(1, 7))
    lag_bin_placement = pd.Timedelta(days=random.randint(1, 5))
    lag_initial_shipment = pd.Timedelta(days=random.randint(1, 10))
    lag_last_shipment = pd.Timedelta(days=random.randint(1, 20))

    # Generate the different dates based on the initial received date
    date_inspected = date_received + lag_inspection
    date_bin_placement = date_received + lag_bin_placement
    date_initial_shipment = date_received + lag_initial_shipment
    date_last_shipment = date_initial_shipment + lag_last_shipment

    return {
        'DateReceived': date_received,
        'DateInspected': date_inspected,
        'DateBinPlacement': date_bin_placement,
        'DateInitialShipment': date_initial_shipment,
        'DateLastShipment': date_last_shipment
    }

# Generate the Fact Table
def generate_inventory_fact_table(num_rows=1000):
    data = []
    for _ in range(num_rows):
        product_lot_receipt_number = fake.unique.ean(length=13)
        product_key = random.randint(1, 50)
        warehouse_key = random.randint(1, 10)
        vendor_key = random.randint(1, 50)

        # Generate lagged dates
        dates = generate_lagged_dates(fake.date_this_year())

        quantity_received = random.randint(100, 500)
        quantity_inspected = random.randint(90, quantity_received)
        quantity_returned_to_vendor = random.randint(0, 10)
        quantity_placed_in_bin = quantity_inspected - quantity_returned_to_vendor
        quantity_shipped_to_customer = random.randint(50, quantity_placed_in_bin)
        quantity_returned_by_customer = random.randint(0, 5)
        quantity_returned_to_inventory = quantity_returned_by_customer
        quantity_damaged = random.randint(0, 5)

        receipt_to_inspected_lag = (dates['DateInspected'] - dates['DateReceived']).days
        receipt_to_bin_placement_lag = (dates['DateBinPlacement'] - dates['DateReceived']).days
        receipt_to_initial_shipment_lag = (dates['DateInitialShipment'] - dates['DateReceived']).days
        initial_to_last_shipment_lag = (dates['DateLastShipment'] - dates['DateInitialShipment']).days

        data.append({
            'ProductLotReceiptNumber': product_lot_receipt_number,
            'ProductKey': product_key,
            'WarehouseKey': warehouse_key,
            'VendorKey': vendor_key,
            'DateReceived': dates['DateReceived'],
            'DateInspected': dates['DateInspected'],
            'DateBinPlacement': dates['DateBinPlacement'],
            'DateInitialShipment': dates['DateInitialShipment'],
            'DateLastShipment': dates['DateLastShipment'],
            'QuantityReceived': quantity_received,
            'QuantityInspected': quantity_inspected,
            'QuantityReturnedToVendor': quantity_returned_to_vendor,
            'QuantityPlacedInBin': quantity_placed_in_bin,
            'QuantityShippedToCustomer': quantity_shipped_to_customer,
            'QuantityReturnedByCustomer': quantity_returned_by_customer,
            'QuantityReturnedToInventory': quantity_returned_to_inventory,
            'QuantityDamaged': quantity_damaged,
            'ReceiptToInspectedLag': receipt_to_inspected_lag,
            'ReceiptToBinPlacementLag': receipt_to_bin_placement_lag,
            'ReceiptToInitialShipmentLag': receipt_to_initial_shipment_lag,
            'InitialToLastShipmentLag': initial_to_last_shipment_lag
        })
    return pd.DataFrame(data)

# Generate all tables
date_dim = generate_date_dimension()
product_dim = generate_product_dimension()
warehouse_dim = generate_warehouse_dimension()
vendor_dim = generate_vendor_dimension()
fact_table = generate_inventory_fact_table()

# Generate bridge tables for each date type
date_received_bridge = generate_date_bridge(fact_table, 'DateReceived')
date_inspected_bridge = generate_date_bridge(fact_table, 'DateInspected')
date_bin_placement_bridge = generate_date_bridge(fact_table, 'DateBinPlacement')
date_initial_shipment_bridge = generate_date_bridge(fact_table, 'DateInitialShipment')
date_last_shipment_bridge = generate_date_bridge(fact_table, 'DateLastShipment')

# Save to Excel files in the specified directory
output_directory = os.path.expanduser("~/Documents")
date_dim.to_excel(os.path.join(output_directory, 'date_dimension.xlsx'), index=False)
product_dim.to_excel(os.path.join(output_directory, 'product_dimension.xlsx'), index=False)
warehouse_dim.to_excel(os.path.join(output_directory, 'warehouse_dimension.xlsx'), index=False)
vendor_dim.to_excel(os.path.join(output_directory, 'vendor_dimension.xlsx'), index=False)
fact_table.to_excel(os.path.join(output_directory, 'inventory_fact_table.xlsx'), index=False)

# Save the bridge tables
date_received_bridge.to_excel(os.path.join(output_directory, 'date_received_bridge.xlsx'), index=False)
date_inspected_bridge.to_excel(os.path.join(output_directory, 'date_inspected_bridge.xlsx'), index=False)
date_bin_placement_bridge.to_excel(os.path.join(output_directory, 'date_bin_placement_bridge.xlsx'), index=False)
date_initial_shipment_bridge.to_excel(os.path.join(output_directory, 'date_initial_shipment_bridge.xlsx'), index=False)
date_last_shipment_bridge.to_excel(os.path.join(output_directory, 'date_last_shipment_bridge.xlsx'), index=False)

print(f"Data generated and saved to {output_directory}.")
