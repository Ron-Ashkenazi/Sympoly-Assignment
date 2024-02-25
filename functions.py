import json
from iso4217 import Currency

def parse_createdAt_or_Status(key, value):
    if key == "CreatedAt":
        date = f"{value[:4]}-{value[4:6]}-{value[6:8]} {value[8:10]}:{value[10:12]}:{value[12:]}"
        return date
    else:
        status_map = {'0': 'Draft', '1': 'Submitted', '2': 'Approved', '3': 'Rejected'}
        return status_map.get(value, 'Unknown')

def parse_transaction_data(data_str):
    date_str = data_str[:14]
    type_str = data_str[14]
    amount_str = data_str[15:-3]
    currency_str = Currency(data_str[-3:]).currency_name

    date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} {date_str[8:10]}:{date_str[10:12]}:{date_str[12:]}"

    amount = float(amount_str.replace(',', '.'))

    return {
        "Date": date,
        "Type": "Credit" if type_str == 'C' else "Debit",
        "Amount": amount,
        "Currency": currency_str
    }


def parse_exrf(content):
    def parse_block(lines, start=0):
        data = {}
        i = start
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith(':') and line.endswith(':') and not line.endswith('::'):
                # Start of a block
                block_name = line[1:-1].strip()
                block_content, i = parse_block(lines, i + 1)
                data[block_name] = block_content
            elif line.startswith('::') and line.endswith('::'):
                # End of a block
                return data, i
            elif line.startswith('[') and not line.endswith(']]'):
                # Start of a list
                list_name = line[1:-1].strip()
                list_content, i = parse_list(lines, i + 1)
                data[list_name] = list_content
            elif '::' in line:
                # Field
                key, value = line.split('::', 1)
                if key.strip() == "CreatedAt" or key.strip() == "Status":
                    data[key.strip()] = parse_createdAt_or_Status(key, value)
                else:
                    data[key.strip()] = value.strip()
            i += 1
        return data, i

    def parse_list(lines, start=0):
        items = []
        item = {}
        i = start
        while i < len(lines):
            line = lines[i].strip()
            if line == '::::':
                # Separator for items in the list
                if item:  # Add the current item to the list and reset for the next item
                    items.append(item)
                    item = {}
            elif line.startswith('[[') and line.endswith(']]'):
                # End of a list
                if item:  # Add the last item if exists
                    items.append(item)
                return items, i
            elif line.startswith(':') and line.endswith(':') and not line.endswith('::'):
                # Nested block within a list item
                block_name = line[1:-1].strip()
                block_content, i = parse_block(lines, i + 1)
                item[block_name] = block_content
            elif line.startswith('[') and not line.endswith(']]'):
                # Nested list within a list item
                list_name = line[1:-1].strip()
                list_content, i = parse_list(lines, i + 1)
                item[list_name] = list_content
            elif '::' in line:
                # Field in a list item
                key, value = line.split('::', 1)
                if key.strip() == "Data":
                    item.update(parse_transaction_data(value.strip()))
                else:   
                    item[key.strip()] = value.strip()
            i += 1
        if item:  # Ensure the last item is added if the list ends without a separator
            items.append(item)
        return items, i

    lines = content.strip().split('\n')
    data, _ = parse_block(lines)
    return data

def read_file(file):
    data = parse_exrf(file)
    json_object = json.dumps(data["Report"])
    return json_object

