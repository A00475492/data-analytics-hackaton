import requests
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Text, Button, END
from ttkthemes import ThemedTk
from tkinter import ttk


# Create a list of tuples containing column names and their unique values
dropdown_options = [
    ('CONDO_OR_RENTAL', ['Rental', 'Apartment']),
    ('DISTRICT_REGION', ['Clayton Park', 'Dartmouth', 'Bedford', 'North End Halifax', 'Outer Halifax', 'South End Halifax', 'West End Halifax', 'Rockingham']),
    ('PARKING_TYPE', ['outdoor', 'Available', 'Not Available', 'street parking', 'underground', 'underground;outdoor', 'underground;covered']),
    ('LAUNDRY_TYPE_PER_SUITE_TYPE', ['In Unit', 'In Building']),
    ('CITY', ['Halifax', 'Dartmouth', 'Bedford'])
]

# Main window with a theme
root = ThemedTk(theme="equilux")
root.title("Rental Rates Dashboard")

# Styling
style = ttk.Style(root)
style.configure('TLabel', font=('Helvetica', 12))
style.configure('TEntry', font=('Helvetica', 12))
style.configure('TButton', font=('Helvetica', 12))
style.configure('TText', font=('Helvetica', 12))
style.configure('TCombobox', font=('Helvetica', 12))

# Address input
address_label = ttk.Label(root, text="Address:")
address_label.pack(pady=5)
address_entry = ttk.Entry(root, width=50)
address_entry.pack(pady=5)

# Unit type input
unit_type_label = ttk.Label(root, text="Unit Type:")
unit_type_label.pack(pady=5)
unit_type_entry = ttk.Entry(root, width=50)
unit_type_entry.pack(pady=5)

# Dictionary to hold dropdown menus
dropdowns = {}

# Create dropdown menus
for column_name, values in dropdown_options:
    label = ttk.Label(root, text=f"{column_name}:")
    label.pack(pady=5)
    
    dropdown = ttk.Combobox(root, values=values, state="readonly")
    dropdown.pack(pady=5)
    
    # Store dropdown in dictionary using column name as key
    dropdowns[column_name] = dropdown

# Function to get competitor rates
def get_rates():
    # Fetch user inputs
    address = address_entry.get()
    unit_type = unit_type_entry.get()
    
    # Fetch dropdown values using dictionary and column names
    condo_or_rental = dropdowns.get('CONDO_OR_RENTAL').get()
    district_region = dropdowns.get('DISTRICT_REGION').get()
    parking_type = dropdowns.get('PARKING_TYPE').get()
    laundry_type = dropdowns.get('LAUNDRY_TYPE_PER_SUITE_TYPE').get()
    city = dropdowns.get('CITY').get()
        
    # Check if any of the dropdown values are None
    if not (condo_or_rental and district_region and parking_type and laundry_type and city):
        results.delete('1.0', END)
        results.insert(END, "Please fill in all dropdown values.")
        return
    
    # Send GET request to the getCompetitorRates endpoint
    response = requests.get(f"http://127.0.0.1:5000/rental/getCompetitorRates?address={address}&unitType={unit_type}")
    if response.status_code == 200:
        results.delete('1.0', END)
        data = response.json()
        if data.get('average_competitor_rent'):
            for builder in data['average_competitor_rent']:
                results.insert(END, f"Builder: {builder['builder']}\nRent: ${builder['rent']:.2f}\n\n")
            plot_data(data['average_competitor_rent'])
        else:
            results.insert(END, "No data available.")
    else:
        results.delete('1.0', END)
        results.insert(END, "Error fetching rates. Please try again.")


# Function to get predicted rent
def get_predicted_rent():
    # Fetch dropdown values using dictionary and column names
    condo_or_rental = dropdowns.get('CONDO_OR_RENTAL').get()
    district_region = dropdowns.get('DISTRICT_REGION').get()
    parking_type = dropdowns.get('PARKING_TYPE').get()
    laundry_type = dropdowns.get('LAUNDRY_TYPE_PER_SUITE_TYPE').get()
    city = dropdowns.get('CITY').get()
    
    # Validate inputs
    if not (condo_or_rental and district_region and parking_type and laundry_type and city):
        results.delete('1.0', END)
        results.insert(END, "Please fill in all dropdown values.")
        return
    
    # Define payload for the POST request
    payload = {
    "condo_or_rental": "Rental",
    "region": "Clayton Park",
    "parking_type": "outdoor",
    "laundry": "In Unit",
    "city": "Halifax",
    "beds": 2,
    "size_sqft": 1129,
    "price_per_sqft": 2.53,
    "transit_score": 4,
    "latitude": 44.65687,
    "longitude": -63.64882,
    "baths": 1.0,
    "walk_score": 71,
    "no_of_utilities": 4,
    "no_of_amenities": 3
    }   
    
    # Send POST request to the getPredictedRent endpoint
    response = requests.post("http://127.0.0.1:5000/rental/getPredictedRent", json=payload)
    
    if response.status_code == 200:
        # Get the predicted rent value from the response
        predicted_rent = response.json()
        
        # Display the predicted rent in the results text area
        results.delete('1.0', END)
        results.insert(END, f"Predicted Rent: ${predicted_rent}")
        
        # Plot the predicted rent
        plot_data([{"builder": "Predicted Rent", "rent": float(predicted_rent)}])
    else:
        # Handle error case
        results.delete('1.0', END)
        results.insert(END, "Error fetching predicted rent. Please try again.")


# Function to plot the data
def plot_data(data):
    try:
        # Extract builder names and rents from the data
        builders = [builder['builder'] for builder in data]
        rents = [builder['rent'] for builder in data]

        # Plot the data
        fig, ax = plt.subplots()  # Use subplots to get the axis object
        ax.bar(builders, rents, color='cornflowerblue')
        ax.set_xlabel('Builder')
        ax.set_ylabel('Rent')
        ax.set_title('Average Competitor Rent by Builder in the Neighbourhood')
        plt.xticks(rotation=45, ha='right')

        # Add rent value text on top of each bar
        for i, rent in enumerate(rents):
            # Place text at the center of the bar (i + 0.5 for better centering)
            ax.text(i, rent, f"${rent:.2f}", ha='center', va='bottom', fontsize=10, color='black')

        plt.tight_layout()
        plt.show()
    except KeyError as e:
        print(f"KeyError: {e} - Ensure that the data structure matches the expected format.")
    except Exception as e:
        print(f"Error plotting data: {e}")



# Get rates button
get_rates_button = ttk.Button(root, text="Get Rates", command=get_rates)
get_rates_button.pack(pady=10)

# Get predicted rent button
get_predicted_rent_button = ttk.Button(root, text="Get Predicted Rent", command=get_predicted_rent)
get_predicted_rent_button.pack(pady=10)

# Results display
results = Text(root, height=10, width=50)
results.pack(pady=10)

# Run the application
root.mainloop()
