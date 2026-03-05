import socket


# Connection to Pit Wall
HOST = "127.0.0.1"
PORT = 8821

RED = "\033[91m"
RESET = "\033[0m"
W_BLUE = "\033[94m"
BOLD = "\033[1m"
CYAN = "\033[96m"

# Williams Metrics: SPD (Speed), BRK (Brake), GFC (G-Force)
METRICS = ["SPD", "BRK", "GFC","FTM","ERS","TYR","RPM"]

MENU_TEXT = """
--- WILLIAMS FW46 TELEMETRY INTERFACE ---
Authorized Metrics:
  > MECHANICAL: SPD (Speed), BRK (Braking), RPM (Engine Revs)
  > THERMAL:    FTM (Fuel Temp), TYR (Tyre Temp)
  > SYSTEMS:    ERS (Battery %), GFC (G-Force), SC (Deploy Safety Car)
  > COMMANDS:   STATUS (Summary), HELP (Menu), EXIT (Close)\n
"""

def check_value(metric,val):
    """ Validates that telemetry value is numeric and physically possible """
    # TO DO: Check if value is a valid number
    try:
        f_val = float(val)
    except ValueError:
        return False
    # TO DO: Ensure it's within race parameters (e.g., 0-360 km/h)
    metric = metric.upper()
    if metric == "SPD":
        if f_val <=450 and f_val >= 0:
            return True
    elif metric == "BRK":
        if f_val >= 0 and f_val <= 170:
            return True
    elif metric == "GFC":
        if f_val >= -7.0 and f_val <= 20.0:
            return True
    elif metric == "FTM":
        if f_val >= -10.0 and f_val <= 115.0:
            return True
    elif metric == "TYR":
        if f_val >= 0 and f_val <= 150.0:
            return True
    elif metric == "ERS":
        if f_val >= 0 and f_val <= 100.0:
            return True
    elif metric == "RPM":
        if f_val >= -0 and f_val <= 15500.0:
            return True
    return False


def check_metric(metric):
    """ Validates the metric code against the Williams authorized list """
    if metric in METRICS:
        return True
    return False

def get_sync_data():
    """ Fetches environment data from the server at startup """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.send("SYNC".encode())
        data = s.recv(1024).decode()
        s.close()
        return data.split("|") # Returns [Track, Session, Weather, Temp]
    except:
        return ["Unknown", "Unknown", "Unknown", "??"]

def main():
    print(f"\n{W_BLUE}{BOLD}Welcome to the Williams pit wall!{RESET}\n")
    # FETCH SYNC DATA
    track, session, weather, temp = get_sync_data()
    print(f"{CYAN}LIVE FROM: {track.upper()} - {session.upper()}{RESET}")
    print(f"CONDITIONS: {weather} ({temp}°C)")
    print("-" * 45)
    print(MENU_TEXT)
    while True:
        # TO DO: Get user input for telemetry packet
        # TO DO: Split input to validate DriverID, Metric, and Value
        # Expected Format: [DriverID] [Metric] [Value]
        # Example: 23 SPD 320

        packet = input("Enter car number, telemetry packet, and value (or 'exit'/'help'): ")
        if packet.upper() == 'EXIT':
            break
        if packet.upper() in ["STATUS", "SC", "HELP"]:
            if packet.upper() == "HELP":
                print(MENU_TEXT)
                continue
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((HOST, PORT))
                client_socket.send(packet.upper().encode())
                print(client_socket.recv(1024).decode())
                client_socket.close()
                continue
            except:
                print("Error: Server Offline.")
                continue

        parts = packet.split(" ")
        if len(parts) != 3:
            print("Invalid format. Use: [ID] [Metric] [Value]")
            continue
        driver_id, metric, value = parts[0], parts[1].upper(), parts[2]

        if check_metric(metric) and check_value(metric,value):
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((HOST, PORT))

                client_socket.send(packet.encode())
                print(f"Server Response: {client_socket.recv(1024).decode()}")

                client_socket.close()
            except ConnectionRefusedError:
                print("Error: Pit Wall Server is offline.")
        else:
            print(f"{RED}Invalid Data: Check your metric code or values.{RESET}")
        pass

if __name__ == "__main__":
    main()