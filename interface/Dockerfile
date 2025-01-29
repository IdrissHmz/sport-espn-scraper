# Use an official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y libaio1 wget unzip

# Install Oracle Instant Client
RUN wget https://download.oracle.com/otn_software/linux/instantclient/2370000/instantclient-basic-linux.x64-23.7.0.25.01.zip -O instantclient.zip \
    && unzip instantclient.zip -d /opt/oracle \
    && rm instantclient.zip

# Set environment variables for Oracle Client
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_23_7:$LD_LIBRARY_PATH
ENV PATH=/opt/oracle/instantclient_23_7:$PATH

# Copy the application files
COPY requirements.txt .
COPY app.py .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
