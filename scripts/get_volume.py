#!/usr/bin/env python

import sys
import json

if sys.version_info[0] == 3:
    import urllib.request as request
else:
    import urllib2 as request

NVIDIA_DOCKER_HOST = 'localhost:3476'
resp = request.urlopen('http://{0}/docker/cli/json'.format(NVIDIA_DOCKER_HOST)).read().decode()
cuda_config = json.loads(resp)

volume = cuda_config['Volumes'][0].split(':')[0]

print(volume)
