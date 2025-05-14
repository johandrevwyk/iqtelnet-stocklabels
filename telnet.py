import socket
import csv
import textwrap
import time
import sys
import os

#just to enable colors for readability on cmd window
if sys.platform == "win32":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

HOST = '0.0.0.0'
PORT = 2323
SQL_FILE = 'label_updates.sql'
STOCK_FILE = 'stock.txt'

# vt100 - cipherlab 8231
HORIZONTAL_SCROLL_STEPS = 19
CLEAR_SCREEN = b"\x1b[2J\x1b[H"

stock_data = {}
processed_barcodes = set()

def load_stock_data():
    stock_data.clear()
    try:
        with open(STOCK_FILE, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                barcode = row[1]
                description = row[3]
                stock_data[barcode] = {'Code': row[0], 'Description': description}

        if not stock_data:
            print("\033[31m[ERROR]\033[0m Stock file is empty")
            sys.exit(1)

        print(f"\033[33m[INFO]\033[0m Loaded {len(stock_data)} stock items into memory.")

    except FileNotFoundError:
        print(f"\033[31m[ERROR]\033[0m {STOCK_FILE} was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"\033[31m[ERROR]\033[0m Error loading stock data: {e}")
        sys.exit(1)

def sanitize_input(raw):
    return raw.decode(errors='ignore').replace('\r', '').replace('\n', '').strip()

def receive_line(conn):
    buffer = b''
    while True:
        chunk = conn.recv(1)
        if not chunk or chunk in [b'\n', b'\r']:
            break
        buffer += chunk
    return buffer

def wrap_text(text, line_length=HORIZONTAL_SCROLL_STEPS):
    wrapper = textwrap.TextWrapper(width=line_length, break_long_words=False, expand_tabs=False, replace_whitespace=False)
    return wrapper.wrap(text)

def display_text_on_scanner(conn, lines):
    for line in lines:
        wrapped_lines = wrap_text(line)
        for wrapped in wrapped_lines:
            conn.sendall(wrapped.encode() + b'\r\n')

def clear_screen(conn):
    conn.sendall(CLEAR_SCREEN)

def get_product_info(barcode):
    product = stock_data.get(barcode)
    if product:
        return [
            f"CODE: {product['Code']}",
            f"BARCODE: {barcode}",
            f"DESC: {product['Description']}"
        ]
    else:
        return ["Product not found."]

def start_telnet_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"\033[33m[INFO]\033[0m Telnet server listening on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            print(f"\033[32m[TELNET]\033[0m Connected by {addr}")
            with conn:
                try:
                    while True:
                        conn.sendall(b"Scan Barcode:\n ")
                        barcode_raw = receive_line(conn)
                        if not barcode_raw:
                            break
                        barcode = sanitize_input(barcode_raw)
                        if not barcode:
                            break

                        clear_screen(conn)

                        if barcode in processed_barcodes:
                            conn.sendall(b"\nAlready processed.")
                            conn.sendall(b"\n\nEnter to retry...\n")
                            receive_line(conn)
                            clear_screen(conn)
                            continue

                        clear_screen(conn)

                        product_info = get_product_info(barcode)
                        conn.sendall(b"\n")
                        display_text_on_scanner(conn, product_info)

                        if any("Product not found" in line for line in product_info):
                            conn.sendall(b"\nEnter to retry...\n")
                            receive_line(conn)
                            clear_screen(conn)
                            continue

                        conn.sendall(b"\nEnter to continue...\n")
                        receive_line(conn)

                        while True:
                            clear_screen(conn)
                            conn.sendall(b"\nQuantity:\n ")
                            quantity_raw = receive_line(conn)
                            quantity = sanitize_input(quantity_raw)

                            if not quantity.isdigit():
                                conn.sendall(b"\nInvalid input.")
                                conn.sendall(b"\n\nEnter to retry...\n")
                                receive_line(conn)
                                continue

                            qty_int = int(quantity)
                            if qty_int < 1 or qty_int > 1000:
                                conn.sendall(b"\nInvalid quantity.")
                                conn.sendall(b"\n\nEnter to retry...\n")
                                receive_line(conn)
                                continue

                            break

                        sql_line = f"UPDATE Stock SET LABELS = {qty_int}, LabelsMustPrint = TRUE WHERE BARCODE = '{barcode}';\n"
                        with open(SQL_FILE, 'a') as sql_file:
                            sql_file.write(sql_line)

                        print(f"\033[36m[ITEM]\033[0m {product_info} - {qty_int}")

                        clear_screen(conn)
                        conn.sendall(b"\nSaved")
                        time.sleep(1)
                        clear_screen(conn)

                        processed_barcodes.add(barcode)

                except Exception as e:
                    print(f"\033[31m[ERROR]\033[0m {e}")
                    try:
                        conn.sendall(b"\nAn error occurred. Disconnecting...\n")
                    except:
                        pass

if __name__ == '__main__':
    load_stock_data()
    start_telnet_server()
