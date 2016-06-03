#!/usr/bin/env python
"""Export case subjects as CSV"""

import csv 
import json
import sys

if __name__ == "__main__":
    fieldnames = [
        'log_number',
        'subject',
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()

    cases = json.loads(sys.stdin.read()) 
    for case in cases:
        log_number = case['log_number']
        for subject in case['subjects']:
            writer.writerow({
                'log_number': log_number,
                'subject': subject,
            })
