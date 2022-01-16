FROM runsascoded/mf-pip-issue
RUN useradd -m user
USER user
ENV USER=user
WORKDIR /home/user
ADD s3_flow_test.py ./
