# Using Selenium With Python in a Docker Container

FROM python:3.6
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
RUN apt-get -y update

# Magic happens
RUN apt-get install -y google-chrome-stable


# Pulling the Image and Setting Up Google Chrome

# Installing Unzip
RUN apt-get install -yqq unzip

# Download the Chrome Driver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip

# Unzip the Chrome Driver into /usr/local/bin directory
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Preparing the Docker for a Run
RUN mkdir -p /workspace/xe_scapper
WORKDIR /workspace/xe_scapper
COPY . /workspace/xe_scapper/
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
