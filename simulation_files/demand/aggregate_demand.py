

def aggregateDemand(files, output_file):

    demand = []

    for f in files:
        with open(f, 'r') as demandFile: 
            demand.extend(demandFile.readlines()[5:-1])
    
    with open(output_file, "w") as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\r\n')
        output.write('<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">\r\n')
        for d in demand:
            output.write(f"{d}")
        output.write('</routes>\r\n')

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("out_file", type=argparse.FileType('w'))
    parser.add_argument('input', type=argparse.FileType('r'), nargs='+')
    args = parser.parse_args()
    print(f"Input files: {[i.name for i in args.input]}")
    print(f"Output file: {args.out_file.name}")
    aggregateDemand([i.name for i in args.input], args.out_file.name)