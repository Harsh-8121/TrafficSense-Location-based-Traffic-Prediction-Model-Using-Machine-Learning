import pandas as pd

print("Traffic Prediction Project Started")

data = pd.read_csv("data/Metro_Interstate_Traffic_Volume.csv")

print("\nDataset loaded successfully!")
print("Number of rows and columns:")
print(data.shape)

print("\nFirst 5 rows:")
print(data.head())