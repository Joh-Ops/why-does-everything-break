import asyncio
import argparse
from time import time

import config
import panos

loop = asyncio.ProactorEventLoop()
asyncio.set_event_loop(loop)


def print_results(results):
    print('-----OUTPUT-----')
    for result in results:
        print(result)
    print('----------------')

def dump_results(results, outfile):
    with open(outfile, 'w+', encoding='utf-8') as f:
        print(f'Outputting results into {f.name}...')
        f.writelines([str(result) + '\n' for result in results])        
    print(f'Finished outputting results into {outfile}')

def get_args():
    parser = argparse.ArgumentParser(description='Scans given iprange for minecraft servers on port 25565.')
    parser.add_argument('option', nargs='*', 
                        help='mode used for scanning: [random, specific, full]')
    parser.add_argument('-f', '--filtering', default=None,
                        help='options for filtering.')
    parser.add_argument('-o', '--outfile', default=None,
                        help='options for filtering.')
    parser.add_argument('-v', '--verbose', type=bool, nargs='?', const=False, default=True)
    parser.add_argument('-s', '--silent', type=bool, nargs='?', const=True, default=False)
    args = parser.parse_args()
    return args

async def main():
    args = get_args()

    option_dict = {'random' : panos.scan_random_aternos,
                   'specific' : panos.scan_specific_aternos,
                   'full' : panos.scan_full_aternos,
                    }
    start = time()
    if args.option[0] != 'full' and len(args.option) == 2:
        option, arg = args.option
        results = await option_dict[option](arg, filtering=args.filtering, silent=args.verbose)
    elif args.option[0] != 'specific':
        option = args.option[0]
        arg = 1
        results = await option_dict[option](filtering=args.filtering, silent=args.verbose)
    else:
        raise ValueError('Did not specify ip')
        
    if args.outfile:
        dump_results(results, args.outfile)
    if not args.silent:
        print_results(results)
        if option == 'random':
            if int(arg) != 1:
                print(f'Scanned {arg} ip ranges.')
            else:
                print('Scanned 1 ip range.')
        elif option == 'full':
            print(f'Scanned {len(config.IPS)} ip ranges.')
                  
        print(f'{len(results)} results.')
        print(f'Took {time()-start} seconds')
        

if __name__ == '__main__':
    loop.run_until_complete(main())
