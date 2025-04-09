FROM public.ecr.aws/docker/library/python:3.12

# Create a project directory inside /app
WORKDIR /home/qnap
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

RUN mkdir -p /home/qnap/asset/chroma_data 

# Add user
ARG USER=qnap
RUN adduser --quiet --uid 100 --gid 101 $USER
RUN chown -R $USER:$GROUP /home/qnap
USER $USER


# Run
CMD ["python", "run.py"]
EXPOSE 8080
