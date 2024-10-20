import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
}

base_url = 'https://www.wondertech.co.ls'
productlinks = []

# Define the Product class
class Product:
    def __init__(self, name=None, ratings=None, reviews=None, price=None):
        self.name = name
        self.ratings = ratings
        self.reviews = reviews
        self.price = price

    def to_dict(self):
        return {
            'name': self.name,
            'ratings': self.ratings,
            'reviews': self.reviews,
            'price': self.price
        }

    def __repr__(self):
        return f"Product(Name: {self.name}, Ratings: {self.ratings}, Reviews: {self.reviews}, Price: {self.price})"

products = []

# Loop through pages
for x in range(1, 4):
    url = f'{base_url}/shop?page={x}'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    productlist = soup.find_all('div', class_='col-lg-4 col-md-6 col-sm-6 pb-1')

    # Find and store unique product links
    for item in productlist:
        for link in item.find_all("a", href=True):
            href = link['href']
            if href not in productlinks and href != 'https://#?':
                # Check if it's a relative URL and complete it
                full_link = href if href.startswith('http') else base_url + href
                productlinks.append(full_link)

# Iterate over product links and fetch product details
for link in productlinks:
    r = requests.get(link, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    
    # Create a dictionary to hold the product attributes
    product_data = {}
    
    # Find product name (h3 tag)
    name_tag = soup.find('h3')
    if name_tag:
        product_data['name'] = name_tag.text.strip()
    
    # Find the review rating (based on stars)
    stars = soup.find_all('small', class_='fas fa-star')
    half_stars = soup.find_all('small', class_='fas fa-star-half-alt')
    if stars or half_stars:
        ratings = len(stars) + (0.5 * len(half_stars))
        product_data['ratings'] = ratings
    
    # Find the number of reviews
    reviews_tag = soup.find('small', class_='pt-1')
    if reviews_tag:
        product_data['reviews'] = reviews_tag.text.strip()
    
    # Find the price
    price_tag = soup.find('h3', class_='font-weight-semi-bold mb-4')
    if price_tag:
        product_data['price'] = price_tag.text.strip()
    
    # Only create a Product object if we have at least one valid attribute
    if product_data:
        product = Product(**product_data)
        products.append(product)
        
# Convert the list of products to a list of dictionaries
product_dicts = [product.to_dict() for product in products]

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(product_dicts)

# Output the DataFrame
print(df)

# To save to a CSV file:
# df.to_csv('products.csv', index=False)