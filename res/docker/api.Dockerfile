FROM python:3.12

# Create a project directory inside /app
WORKDIR /app
# Copy requirements first to leverage Docker cache
COPY res/requirements.txt ./res/

# Install dependencies
RUN pip install -r res/requirements.txt

# Copy application code with proper structure
COPY run.py ./
COPY api ./api/
COPY util ./util/
COPY db ./db/
COPY models ./models/
COPY .env ./

RUN mkdir -p /app/asset/chroma_data 

# Add user
ARG USER=qnap
ARG GROUP=qnap
RUN addgroup --quiet $GROUP
RUN adduser --quiet --ingroup $GROUP $USER
RUN chown -R $USER:$GROUP /app
USER $USER


# Run
CMD ["python", "run.py"]
EXPOSE 8080
