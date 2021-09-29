import pyarrow as pa

fs = pa.hdfs.connect(
    host='192.169.139.137',
    port=8020,
    user='naya',
    kerb_ticket=None,
    driver= 'libhdfs',
    extra_conf=None
)