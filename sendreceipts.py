import argparse
import math
import time

import stripe

TIMESTAMP_FILE = 'timestamp'


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Send receipts for all charges added since this script was last run. Will not send receipts to people who already received receipts")
    parser.add_argument('-k', '--api-key', help="Your stripe secret api key", required=True)
    parser.add_argument('-e', '---recipients', nargs='+', help="recipients for the receipt", required=True)
    return parser.parse_args()


def send_receipt(charge_id, recipients):
    charge = stripe.Charge.retrieve(charge_id)
    charge.receipt_email = ','.join(recipients)
    charge.save()


def get_previous_timestamp():
    try:
        with open(TIMESTAMP_FILE, 'r') as _file:
            timestamp = _file.read()
    except FileNotFoundError:
        return None
    formatted_timestamp = int(math.floor(float(timestamp)))
    return int(formatted_timestamp)


def update_timestamp():
    with open(TIMESTAMP_FILE, 'w') as _file:
        _file.write(str(time.time()))


def get_charges(since=None):
    iterator = stripe.Charge.list(created={'gte': since}).auto_paging_iter()
    return iterator


def run(recipients):
    timestamp = get_previous_timestamp()
    for new_charge in get_charges(timestamp):
        charge_id = new_charge.id
        print(charge_id)
        send_receipt(charge_id, recipients)
    update_timestamp()


if __name__ == '__main__':
    parameters = parse_arguments()
    stripe.api_key = parameters.api_key
    run(parameters.recipients)
