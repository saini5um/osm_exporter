import prometheus_client as prom
import random
from random import randrange
import time
import cx_Oracle

#db_con_string='ordermgmt/osmcluster@den00oli.us.oracle.com/pdbosmsom.us.oracle.com'
db_con_string='ordermgmt/CGBUpassw0rd@10.242.44.23/orcl'
num_order_sql="select count(1) from om_order_header where ord_creation_date > sysdate - 2"
num_compl_order_sql="select count(1) from om_order_header where ord_creation_date > sysdate - 2 and ord_state_id = 7"
num_prog_order_sql="select count(1) from om_order_header where ord_creation_date > sysdate - 2 and ord_state_id = 4"
num_cancel_order_sql="select count(1) from om_order_header where ord_creation_date > sysdate - 2 and ord_state_id = 3"
num_fail_order_sql="select count(1) from om_order_header where ord_creation_date > sysdate - 2 and ord_state_id > 7"
sla_breach_sql="select count(1) from om_order_header where ord_state_id = 4 and sysdate - ord_start_date > 0.5"
som_lifetime_sql="select avg((ord_completion_date - ord_start_date)*24*60) from om_order_header where ord_creation_date > sysdate - 7 and ord_state_id = 7 and cartridge_id = 1066"
tom_lifetime_sql="select avg((ord_completion_date - ord_start_date)*24*60) from om_order_header where ord_creation_date > sysdate - 7 and ord_state_id = 7 and cartridge_id = 1062"
test_sql="select order_seq_id from om_order_header"

con = cx_Oracle.connect('ordermgmt/osmcluster@den00oli.us.oracle.com/pdbosmsom.us.oracle.com')
con = cx_Oracle.connect(db_con_string)
print(con.version)

#con.close()

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
   prom.start_http_server(9005)

   while True:
       cursor = con.cursor()
       cursor.execute(num_order_sql)
#       cursor.execute(test_sql)
       count, = cursor.fetchone()
       print("row:", count)
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
       ltg.labels(role='som').set(count)

       cursor.execute(tom_lifetime_sql)
       count, = cursor.fetchone()
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

#       gauge.set(random.random() * 15 - 5)
       histogram.observe(random.random() * 10)
       summary.observe(random.random() * 10)
       process_request(random.random() * 5)

       time.sleep(15)

