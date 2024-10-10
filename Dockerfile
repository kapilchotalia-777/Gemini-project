# Step 1: Use an official Python runtime as a base image
FROM python:3.11

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container at /app
COPY . /app

# Step 4: Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Make port 5000 available to the world outside this container (if needed)
# Change the port number according to your app’s requirements
EXPOSE 5000

# Step 6: Define the command to run your app using python
CMD ["python", "app.py"]

