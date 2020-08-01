import boto3
import numpy as np
import pandas as pd

route_id = '39'
direction_id = '0'

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('rte-{}-d{}'.format(route_id, direction_id))

still_has_items = True
last_eval_key = None

response = None

# while still_has_items:
response = table.scan()
# still_has_items = False

df = pd.DataFrame(['a'],index=['b'])

print(df)
