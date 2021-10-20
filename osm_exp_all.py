import prometheus_client as prom
import random
from random import randrange
import time
import cx_Oracle
import json

with open('osmexp.cfg1', 'r') as f:
    config = json.load(f)

db_con_string = config['DATABASE']['USERNAME'] + "/" + config['DATABASE']['PASSWORD'] + "@" + config['DATABASE']['HOST'] + "/" + config['DATABASE']['SERVICE']
print(db_con_string)

sleep_time =  config['SLEEPTIME']
http_port = config['HTTP']['PORT']

num_order_sql= config['SQL']['num_order_sql']
num_compl_order_sql= config['SQL']['num_compl_order_sql']
num_prog_order_sql= config['SQL']['num_prog_order_sql']
num_cancel_order_sql= config['SQL']['num_cancel_order_sql']
num_fail_order_sql= config['SQL']['num_fail_order_sql']
sla_breach_sql= config['SQL']['sla_breach_sql']
som_lifetime_sql= config['SQL']['som_lifetime_sql']
tom_lifetime_sql= config['SQL']['tom_lifetime_sql']
test_sql= config['SQL']['test_sql']

con = cx_Oracle.connect(db_con_string)
print(con.version)

req_summary = prom.Summary('python_my_req_example', 'Time spent processing a request')

@req_summary.time()
def process_request(t):
   time.sleep(t)


if __name__ == '__main__':

   counter = prom.Counter('osm_num_order', 'Total number of orders')
   gauge = prom.Gauge('osm_orders_today', 'Total number of orders in the last 24 hours')
   g2 = prom.Gauge('osm_comp_orders_today', 'Total number of orders completed in the last 24 hours')
   g3 = prom.Gauge('osm_sla_breach', 'Total number of orders breached SLA')
   mg = prom.Gauge('osm_orders_metric_today', 'Total number of orders in the last 24 hours', ['state'])
   ltg = prom.Gauge('osm_orders_lifetime', 'Average order life time in the last 7 days', ['role'])
   geog = prom.Gauge('osm_orders_jeopardy', 'Orders in Jeopardy', ['CO'])
   histogram = prom.Histogram('python_my_histogram', 'This is my histogram')
   summary = prom.Summary('python_my_summary', 'This is my summary')
   prom.start_http_server(http_port)

   while True:
       cursor = con.cursor()
       cursor.execute(num_order_sql)
#       cursor.execute(test_sql)
       count, = cursor.fetchone()
#       print("row:", count)
       counter.inc(count)
       gauge.set(count)

       cursor.execute(num_compl_order_sql)
       count, = cursor.fetchone()
       g2.set(count)
       mg.labels(state='completed').set(count)

       cursor.execute(sla_breach_sql)
       count, = cursor.fetchone()
       g3.set(count)

       cursor.execute(num_prog_order_sql)
       count, = cursor.fetchone()
       mg.labels(state='progress').set(count)

       cursor.execute(num_cancel_order_sql)
       count, = cursor.fetchone()
       mg.labels(state='cancel').set(count)

       cursor.execute(num_fail_order_sql)
       count, = cursor.fetchone()
       mg.labels(state='fail').set(count)

       cursor.execute(som_lifetime_sql)
       count, = cursor.fetchone()
       print("som lifetime:", count)
       if count is None:
           count = 0
       ltg.labels(role='som').set(count)

       cursor.execute(tom_lifetime_sql)
       count, = cursor.fetchone()
       if count is None:
           count = 0
       ltg.labels(role='tom').set(count)

       geog.labels(CO='JW').set(randrange(10)*randrange(2))
       geog.labels(CO='TP').set(randrange(10)*randrange(2))
       geog.labels(CO='HG').set(randrange(10)*randrange(2))
       geog.labels(CO='AM').set(randrange(10)*randrange(2))
       geog.labels(CO='BP').set(randrange(10)*randrange(2))
       geog.labels(CO='TS').set(randrange(10)*randrange(2))
       geog.labels(CO='AR').set(randrange(10)*randrange(2))
       geog.labels(CO='OC').set(randrange(10)*randrange(2))

       for count in cursor:
           print("Order count:", count)
#           counter.inc(count)
       cursor.close()

       histogram.observe(random.random() * 10)
       summary.observe(random.random() * 10)
       process_request(random.random() * 5)

       time.sleep(sleep_time)

