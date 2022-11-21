import subprocess
import sys
import time

def parse_args(args):
    sign_args = ['sign']
    stamp_args = ['Timestamp']
    url = 0
    do_stamp = False
    while args:
        a = args[0]
        if a and a[0] == '/':
            if a in ('/q', '/v', '/debug/'):
                # common args
                sign_args.append(a)
                stamp_args.append(a)
                args = args[1:]
            elif a in ('/a', '/as', '/fd', '/nph', '/ph', '/sm', '/uw'):
                sign_args.append(a)
                args = args[1:]
            elif a in ('/ac', '/c', '/csp', '/d', '/du', '/f', '/i', '/kc', '/n', '/p', '/p7', '/p7ce', '/p7co', '/r', '/s', '/sha1', '/u', ):
                sign_args.extend(args[:2])
                args = args[2:]
            elif a in ('/fd'):
                if args[1][0] == '/':
                    sign_args.append(a)
                    args = args[1:]
                else:
                    sign_args.extend(args[:2])
                    args = args[2:]
            elif a in ('/t', '/tr'):
                stamp_args.extend(args[:2])
                args = args[2:]
                do_stamp = True
                url = len(stamp_args) - 1
            elif a in ('/td', '/tp'):
                stamp_args.extend(args[:2])
                args = args[2:]
            else:
                # unknown arg?
                if args[1][0] == '/':
                    sign_args.append(a)
                    args = args[1:]
                else:
                    sign_args.extend(args[:2])
                    args = args[2:]
        else:
            # file
            sign_args.append(a)
            stamp_args.append(a)
            args = args[1:]
    if not do_stamp:
        stamp_args = []
    return (sign_args, stamp_args, url)

def sign(args, delay=1, attempts=100, servers=(), config=None):
    if config:
        delay = float(config['DEFAULT'].get('Wait', delay))
        attempts = float(config['DEFAULT'].get('Attempts', attempts))
        servers = config.sections()
    signtool = ['signtool']
    # args[0] is command
    if args[0] == 'sign':
        sign_args, stamp_args, url_index = parse_args(args[1:])
    elif args[0] == 'Timestamp':
        sign_args, stamp_args, url_index = parse_args(args[1:])
        sign_args = []
    else:
        sign_args = args
        stamp_args = []
        url_index = 0
    if sign_args:
        result = subprocess.run(signtool + list(sign_args), check=False)
        if result.returncode != 0:
            return result.returncode
    if stamp_args:
        result = subprocess.run(signtool + list(stamp_args), capture_output=True, check=False)
        if result.returncode != 0 and attempts and servers:
            for i in range(attempts):
                url = servers[i % len(servers)]
                wait = delay
                if config:
                    wait = float(config[url].get('Wait', delay))
                sys.stdout.write(f'Sleeping for {wait} seconds...\n')
                time.sleep(wait)
                a = list(stamp_args)
                a[url_index] = url
                sys.stdout.write(f'Retrying timestamp with {url}\n')
                result = subprocess.run(signtool + a, capture_output=True, check=False)
                if result.returncode == 0:
                    break
        # Only show last output
        if result.stdout:
            sys.stdout.write(result.stdout.decode('utf8'))
        if result.stderr:
            sys.stderr.write(result.stderr.decode('utf8'))
        return result.returncode
    return 0
