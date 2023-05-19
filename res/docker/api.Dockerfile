FROM python

WORKDIR /app

# add code
ADD *.py /app/
ADD res/requirements.txt /app/

# install dependencies
RUN pip install -r requirements.txt

# add user
ARG USER=qnap
RUN adduser --quiet $USER
RUN chown -R $USER:$USER /app
USER $USER

# run
CMD python run.py
EXPOSE 8080
