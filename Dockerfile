FROM python:3.12.10-alpine3.21

# Install build dependencies for scikit-learn and its dependencies (numpy, scipy)
# build-base includes C/C++ compilers (gcc, g++)
RUN apk add --no-cache build-base gfortran openblas-dev lapack-dev

# Set the working directory
WORKDIR /app
# Copy the requirements file into the container
COPY requirements.txt .
# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Optional: Remove build dependencies after pip install to keep image size smaller
# RUN apk del build-base gfortran openblas-dev lapack-dev

# Copy the rest of the application code into the container
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py"]