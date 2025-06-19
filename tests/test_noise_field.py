#import matplotlib.pyplot as plt
from app.memory import generate_noise_field_opensimplex

# Token eingeben
token = "geheimer_token"

# Noise-Feld generieren
field = generate_noise_field_opensimplex(token, size=100, scale=0.1)

print("Field shape:", field.shape)
print("First row:", field[0])