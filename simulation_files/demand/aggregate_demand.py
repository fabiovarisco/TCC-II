

def aggregateDemandFromPrefix(prefix, max, output_file):

    files = [f"{prefix}{i}.trip.xml" for i in range(1, max + 1)]
    print(f"Input files: {files}")

    aggregateDemand(files, output_file)


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
    #parser.add_argument('input_base', type=argparse.FileType('r'), nargs='+')
    parser.add_argument('input_base')
    parser.add_argument('max')
    args = parser.parse_args()
    print(f"Output file: {args.out_file.name}")
    aggregateDemandFromPrefix(args.input_base, int(args.max), args.out_file.name)
