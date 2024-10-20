"""Read/Save BTLE data."""

import argparse
import datetime
import time

from bleson import Observer
from bleson import get_provider


def main():
    """Entrypoint."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--names',
        nargs='*',
        default=[],
        help='Names of devices to read data from'
    )
    parser.add_argument(
        '--outputs',
        nargs='*',
        choices=['stdout', 'sqlite'],
        default=['stdout'],
        help='Output destinations for data'
    )
    parser.add_argument(
        '-n',
        type=int,
        default=None,
        help='Exit after N data points per name or in total based on --names flag'  # noqa:E501
    )
    parser.add_argument(
        '-t',
        type=int,
        default=30,
        help='Timeout in seconds'
    )
    args = parser.parse_args()

    names = args.names
    outputs = args.outputs
    max_points = args.n
    timeout = args.t

    # store data for exit purposes
    points = dict()

    # handle data point from btle advertisement
    def on_data(data):
        key = str(data.name)

        # filter out according to name
        if names and key not in names:
            return

        # filter out if max data reached
        if max_points:

            if names and len(points.get(key, [])) >= max_points:
                return
            if not names and sum([len(x) for _, x in points.items()]) >= max_points:  # noqa:E501
                return

        # output data
        output(data, outputs)

        # record data as seen
        if key not in points:
            points[key] = []
        points[key].append(data)

    # setup bluetooth adapter
    adapter = get_provider().get_adapter()
    observer = Observer(adapter)
    observer.on_advertising_data = on_data

    # check in on data reception
    start_time = time.time()
    observer.start()
    while True:

        # found all data points, stop
        if max_points:
            if names:
                if len(points.keys()) == len(names) and all([len(x) == max_points for _, x in points.items()]):  # noqa:E501
                    break
            else:
                if sum([len(x) for _, x in points.items()]):
                    break

        time.sleep(1)

        # ran too long, exit
        elapsed_time = time.time() - start_time
        if elapsed_time >= timeout:
            exit_code = 1 if max_points else 0
            exit(exit_code)

    observer.stop()


def c2f(val):
    """Celsius to farenheit."""
    return round(32 + 9 * val / 5, 2)


def output(raw_data, outputs):
    """Output data."""
    formatted_data = format_data(raw_data)
    if 'stdout' in outputs:
        if formatted_data:
            print(formatted_data['to_string'])
        else:
            print(raw_data)
    if 'sqlite' in outputs:
        raise NotImplementedError()


def format_data(data):
    """Format data."""
    if data.name and data.name.startswith('GVH5075'):
        name = data.name
        values = int.from_bytes(data.mfg_data[3:6], 'big')
        temp_c = float(values / 10000)
        temp_f = c2f(temp_c)
        hum = float((values % 1000) / 10)
        battery = data.mfg_data[6]
        now = datetime.datetime.now().isoformat()
        to_string = f'{now} | {name} | {temp_c}°C | {temp_f}°F | {hum}% | {battery}'  # noqa:E501
        return {
            'temp_c': temp_c,
            'temp_f': temp_f,
            'hum': hum,
            'battery': battery,
            'datetime': now,
            'to_string': to_string
        }
    return None


if __name__ == '__main__':
    main()
