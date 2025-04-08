FROM python:3.12

# Create a project directory inside /app
WORKDIR /app
# Copy requirements first to leverage Docker cache
COPY res/requirements.txt ./res/

# Install dependencies
RUN pip install -r res/requirements.txt

# Copy application code with proper structure
COPY run.py ./
COPY app ./app/
COPY util ./util/
COPY db ./db/
COPY models ./models/
COPY asset ./asset/
COPY .env ./
RUN mkdir -p ./asset/chroma_data

# Add user
ARG USER=qnap
RUN adduser --quiet $USER
RUN chown -R $USER:$USER /app
USER $USER

# Run
CMD ["python", "run.py"]
EXPOSE 8080
