import ast
from datetime import datetime
# import gevent
# from gevent import monkey
# monkey.patch_all()
# from gevent.pool import Pool
import requests
import time

def get_uve_data(url):
  try:
    s = requests.Session()
    data = s.get(url)
    import pdb;pdb.set_trace()
  except Exception as e:
    print(e)


def get_uve_hrefs(uve):
  resp = requests.get(uve)
  if resp:
    resp = ast.literal_eval(resp.content)
    return resp
    print(type(resp))
  return []


def main(uve=''):
#   pool = Pool(4000)
  print('getting uves')
  data = get_uve_hrefs(uve)
  print('Number of port hrefs %s'%len(data))
  urls = []
  jobs = []
  for uve in data:
    urls.append(uve['href'])
  start = datetime.now()
  for url in urls:
    # jobs.append(pool.spawn(get_uve_data,url))
    get_uve_data(url)
  #print('Time to append:%s'%(datetime.now()-start))
#   gevent.joinall(jobs)
  print('Time taken:%s'%(datetime.now()-start))


if __name__ == '__main__':
  main('http://10.204.216.103:8081/analytics/uves/virtual-machine-interfaces')

# Use vnc api to fetch
# In analytics api container's entrypoint, aaa_mode=no-auth and restart