FROM runsascoded/mf-pip-issue-batch
ARG metaflow=2.4.8
RUN pip install metaflow==${metaflow}
RUN useradd -m user
USER user
ENV USER=user
WORKDIR /home/user
ADD s3_flow_test.py ./
ENTRYPOINT [ "python", "s3_flow_test.py" ]
CMD [ "run" ]
