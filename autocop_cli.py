import argparse
import sys
from autocopLite import *

def main():
    parser = argparse.ArgumentParser(description="Process and plot ROCm profile data.")
    
    subparsers = parser.add_subparsers(dest="command")

    # parsers for the single and comparative plot modes
    single_plot_parser = subparsers.add_parser("single_plot", help="Generate a sunburst plot for a single CSV file.")
    single_plot_parser.add_argument("csv_file", type=str, help="Path to the input CSV file.")
    single_plot_parser.add_argument("architecture", type=str, choices=["ROCm", "Nvidia"], help="Architecture type.")
    single_plot_parser.add_argument("output_html", type=str, help="Path to the output HTML file.")

    compare_plot_parser = subparsers.add_parser("compare_plot", help="Generate comparison plots for two CSV files.")
    compare_plot_parser.add_argument("csv_file1", type=str, help="Path to the first input CSV file.")
    compare_plot_parser.add_argument("arch1", type=str, choices=["ROCm", "Nvidia"], help="Architecture type for the first CSV file.")
    compare_plot_parser.add_argument("csv_file2", type=str, help="Path to the second input CSV file.")
    compare_plot_parser.add_argument("arch2", type=str, choices=["ROCm", "Nvidia"], help="Architecture type for the second CSV file.")
    compare_plot_parser.add_argument("output_html", type=str, help="Path to the output HTML file.")

    args = parser.parse_args()
    
    autocop = AutocopLite()
    
    if args.command == "single_plot":
        autocop.process_and_plot(args.csv_file, args.architecture, args.output_html)
    elif args.command == "compare_plot":
        autocop.process_and_compare(args.csv_file1, args.arch1, args.csv_file2, args.arch2, args.output_html)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
