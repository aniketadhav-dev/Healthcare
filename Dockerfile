# Step 1: Base image
FROM python:3.9-slim

# Step 2: Working directory set karein
WORKDIR /app

# Step 3: Dependencies copy aur install karein
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Pura project code copy karein
COPY . .

# Step 5: Backend directory mein move karein taaki imports sahi kaam karein
WORKDIR /app/backend

# Step 6: Environment variable for Port
ENV PORT=8000

# Step 7: App start karein
# Hum app.py chala rahe hain jo backend + frontend dono handle karega
CMD ["python", "main.py"]