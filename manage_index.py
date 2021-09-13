from modules import index
import argparse

commands = ["cleanup", "re-index"]

parser = argparse.ArgumentParser(description='Manager for the Inverted Index.')
parser.add_argument('command', choices=commands, help='Command to perform on index.')
parser.add_argument('-s3', '--in_s3', action='store_true', help='If passed, the index will be loaded from the S3 bucket')
parser.add_argument('-fp', '--file_path', nargs='?', const='index.json', help='The file path for the index.')

args = parser.parse_args()
inv_index = index.InvertedIndex(from_file=True, in_s3=args.in_s3, file_path=args.file_path or 'index.json')
if args.command == "cleanup":
    inv_index.cleanup()