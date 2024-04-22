import streamlit as st
import requests
import matplotlib.pyplot as plt

# Create a list of tuples containing column names and their unique values
dropdown_options = [
    ('CONDO_OR_RENTAL', ['Rental', 'Apartment']),
    ('DISTRICT_REGION', ['Clayton Park', 'Dartmouth', 'Bedford', 'North End Halifax', 'Outer Halifax', 'South End Halifax', 'West End Halifax', 'Rockingham']),
    ('PARKING_TYPE', ['outdoor', 'Available', 'Not Available', 'street parking', 'underground', 'underground;outdoor', 'underground;covered']),
    ('LAUNDRY_TYPE_PER_SUITE_TYPE', ['In Unit', 'In Building']),
    ('CITY', ['Halifax', 'Dartmouth', 'Bedford'])
]

# Main title
st.title("Rental Rates Dashboard")

# Form inputs
address = st.text_input("Address:")
unit_type = st.text_input("Unit Type:")

# Dictionary to hold dropdown widgets
dropdowns = {}

# Create dropdown widgets
for column_name, values in dropdown_options:
    dropdowns[column_name] = st.selectbox(f"{column_name}:", values)

# Function to get competitor rates
def get_rates():
    # Fetch user inputs
    address_value = address
    unit_type_value = unit_type
    dropdown_values = {key: value for key, value in dropdowns.items()}
    
    # Send GET request to the getCompetitorRates endpoint
    response = requests.get(f"http://127.0.0.1:5000/rental/getCompetitorRates",
                            params={"address": address_value, "unitType": unit_type_value, **dropdown_values})
    if response.status_code == 200:
        data = response.json()
        if data.get('average_competitor_rent'):
            st.write("Average Competitor Rent:")
            for builder in data['average_competitor_rent']:
                st.write(f"Builder: {builder['builder']}, Rent: ${builder['rent']:.2f}")
            plot_data(data['average_competitor_rent'])
        else:
            st.error("No data available.")
    else:
        st.error("Error fetching rates. Please try again.")

# Function to get predicted rent
def get_predicted_rent():
    # Fetch user inputs
    dropdown_values = {key: value for key, value in dropdowns.items()}
    
    # Send POST request to the getPredictedRent endpoint
    response = requests.post("http://127.0.0.1:5000/rental/getPredictedRent", json=dropdown_values)
    
    if response.status_code == 200:
        # Get the predicted rent value from the response
        predicted_rent = response.json().get('predicted_rent')
        
        # Display the predicted rent in the results area
        st.write(f"Predicted Rent: ${predicted_rent}")
    else:
        # Handle error case
        st.error("Error fetching predicted rent. Please try again.")

# Function to plot the data
def plot_data(data):
    builders = [builder['builder'] for builder in data]
    rents = [builder['rent'] for builder in data]

    # Plot the data
    fig, ax = plt.subplots()
    ax.bar(builders, rents, color='cornflowerblue')
    ax.set_xlabel('Builder')
    ax.set_ylabel('Rent')
    ax.set_title('Average Competitor Rent by Builder in the Neighbourhood')
    plt.xticks(rotation=45, ha='right')

    # Add rent value text on top of each bar
    for i, rent in enumerate(rents):
        ax.text(i, rent, f"${rent:.2f}", ha='center', va='bottom', fontsize=10, color='black')

    st.pyplot(fig)

# Get rates button
get_rates_button = st.button("Get Rates", on_click=get_rates)

# Get predicted rent button
get_predicted_rent_button = st.button("Get Predicted Rent", on_click=get_predicted_rent)
