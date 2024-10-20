# btle-tools

Command line script to listen for and save low energy bluetooth data, specifically for Govee thermometers. Inspired by [this gist](https://gist.github.com/tchen/65d6b29a20dd1ef01b210538143c0bf4).

### Setup

Create virtual environment and install packages
```
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

Enable running not as root [docs reference](https://bleson.readthedocs.io/en/latest/installing.html#linux)
```
$ sudo setcap cap_net_raw,cap_net_admin+eip $(eval readlink -f `which python`)
```

Make sure adapter is enabled (raspberry pi3)

```
$ rfkill list
$ rfkill unblock {id}
```

### Running

```
usage: run.py [-h] [--names [NAMES ...]] [--outputs [{stdout,sqlite} ...]] [-n N] [-t T]

optional arguments:
  -h, --help            show this help message and exit
  --names [NAMES ...]   Names of devices to read data from (default: [])
  --outputs [{stdout,sqlite} ...]
                        Output destinations for data (default: ['stdout'])
  -n N                  Exit after N data points per name or in total based on --names flag (default: None)
  -t T                  Timeout in seconds (default: 30)
```


#### Examples

Print all incoming data
```
$ python run.py
```

Filter data by name, gather 1 data point per device name, timeout after 60s
```
$ python run.py --names GVH5075_8A5E GVH5075_B8BB GVH5075_8AEF GVH5075_75F7 -n 1 -t 60
```

Save data to database (future feature)
