import socket
import datetime
from telemetry_client import check_value
import random

# Pit Wall Configuration
HOST = "127.0.0.1"
PORT = 8821

total_packets = 0
max_speed = 0
alerts_triggered = 0

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"
W_BLUE = "\033[94m"
BOLD = "\033[1m"

fuel_level = 100.0
tyre_life = 100.0

DRIVERS = {
    "23": "ALBON",
    "55": "SAINZ",
    "0": "TEST_BENCH"
}

# The "Virtual Garage" - keeps cars independent
CAR_DATA = {
    "23": {"name": "ALBON", "fuel": 100.0, "tyre": 100.0, "max_spd": 0.0},
    "55": {"name": "SAINZ", "fuel": 100.0, "tyre": 100.0, "max_spd": 0.0},
    "0":  {"name": "TEST_BENCH", "fuel": 100.0, "tyre": 100.0, "max_spd": 0.0}
}

# Weather Scenarios: {Condition: [Min Temp, Max Temp]}
WEATHER_PROFILES = {
    "Sunny": [35, 52],
    "Overcast": [22, 30],
    "Light Rain": [15, 21],
    "Stormy": [10, 14]
}

# Full F1 Calendar
TRACKS = [
    "Bahrain", "Saudi Arabia", "Australia", "Japan", "China", "Miami",
    "Emilia Romagna", "Monaco", "Canada", "Spain", "Austria", "Great Britain",
    "Hungary", "Belgium", "Netherlands", "Italy", "Azerbaijan", "Singapore",
    "USA (Austin)", "Mexico", "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"
]

# Specific Session Formats
SESSIONS = [
    "Testing", "Practice 1", "Practice 2", "Practice 3",
    "Q1", "Q2", "Q3", "SQ1", "SQ2", "SQ3", "Sprint", "RACE"
]

#Randomly pick the weather when the server starts
current_condition = random.choice(list(WEATHER_PROFILES.keys()))
temp_range = WEATHER_PROFILES[current_condition]
track_temp = random.randint(temp_range[0], temp_range[1])
# Randomly pick the event details when the server starts
current_track = random.choice(TRACKS)
current_session = random.choice(SESSIONS)
safety_car_active = False # Starts as False

start_time_str = datetime.datetime.now().strftime("%H-%M")
log_filename = f"williams_{current_track}_{current_session}_{start_time_str}.log".lower().replace(" ", "_")

def handle_request(data):
    global total_packets, max_speed, alerts_triggered, safety_car_active, fuel_level, tyre_life

    if data.upper() == "SYNC":
        return f"{current_track}|{current_session}|{current_condition}|{track_temp}"

    # Check for Status request
    if data.upper() == "STATUS":
        # 1. Global Header (Environment)
        sc_display = f"{RED}ACTIVE{RESET}" if safety_car_active else f"{GREEN}NONE{RESET}"

        summary = f"\n{CYAN}{BOLD}--- WILLIAMS {current_session.upper()} REPORT ---{RESET}\n"
        summary += f"LOCATION:   {current_track}\n"
        summary += f"WEATHER:    {current_condition} ({track_temp}°C)\n"
        summary += f"SAFETY CAR: {sc_display}\n"
        summary += f"{CYAN}{'-' * 40}{RESET}\n"

        # 2. Individual Car Data (The "Garage" Loop)
        for car_id, info in CAR_DATA.items():
            summary += f"[#{car_id} {info['name']}]\n"
            summary += f"   FUEL: {info['fuel']:.1f}% | TYRE: {info['tyre']:.1f}% | MAX: {info['max_spd']} km/h\n"

        # 3. Global Stats Footer
        summary += f"{CYAN}{'-' * 40}{RESET}\n"
        summary += f"TOTAL PACKETS:    {total_packets}\n"
        summary += f"ALERTS TRIGGERED: {alerts_triggered}\n"
        summary += f"{CYAN}{'=' * 40}{RESET}\n"

        return summary

    if data.upper() == "SC":
        safety_car_active = not safety_car_active  # Flips True to False or vice-versa
        status_msg = "DEPLOYED" if safety_car_active else "CLEARED"
        return f"{YELLOW}--- SAFETY CAR {status_msg} ---{RESET}"

    parts = data.split(" ")
    driver_id = parts[0]
    metric = parts[1]
    val = parts[2]

    # Use the driver_id to get the specific car's dictionary
    car = CAR_DATA.get(driver_id)
    if car:
        driver_name = car["name"]

        # --- UPDATE CAR PHYSICS ---
        car["fuel"] -= 2.5  # Constant fuel burn
        car["tyre"] -= 2.5  # Constant physical wear

        if metric.upper() == "TYR":
            car["tyre"] -= 4.0  # Rubber wear
        if car["tyre"] < 30:
            status = "WARNING: HIGH TYRE DEGRADATION"
            color = RED

        if metric.upper() == "SPD" and float(val) > car["max_spd"]:
            car["max_spd"] = float(val)
            car["tyre"] -= 4.0
            car["fuel"] -= 2.5

        # Add a low fuel warning tag to the end of the report if needed
        fuel_warning = f" | {RED}[LOW FUEL: {car['fuel']:.1f}%]{RESET}" if car["fuel"] < 10.0 else ""
    else:
        # If the car ID isn't 23 or 55
        driver_name = "UNKNOWN_DRIVER"
        fuel_warning = ""

    # 2. Get high-precision timestamp
    now = datetime.datetime.now()
    log_date = now.strftime("%Y-%m-%d")
    log_time = now.strftime("%H:%M:%S.%f")[:-3]

    if check_value(metric, val):
        total_packets += 1 # Count the packet
        car["fuel"] -= 2.0  # Each packet consumes a tiny bit of fuel
        if car["fuel"] <= 0:
            car["fuel"] = 0
            return f"{RED}!!! CRITICAL: CAR HAS RUN OUT OF FUEL - ENGINE STALL !!!{RESET}"
        if metric == "RPM" and float(val) > 12000:
            car["fuel"] -= 5.0
        if car["fuel"] < 5.0:
            # This will add a warning to the standard telemetry response
            fuel_warning = f" | {RED}[LOW FUEL: {fuel_level:.1f}%]{RESET}"
        else:
            fuel_warning = ""
        status = "NOMINAL"
        color = GREEN
        f_val = float(val)
        if metric.upper() == "TYR":
            car["tyre"] -= 5.0  # Every time you check temp, the tyre wears down
            if car["tyre"] < 30.0:
                status = "WARNING: HIGH TYRE DEGRADATION"
                color = YELLOW
        # Logic for the "Status Flags"
        if metric.upper() == "SPD" and f_val > car["max_spd"]:
            car["max_spd"] = f_val
        if metric.upper() == "FTM":
            if f_val > 95.0:  # Critical threshold for fuel volatility
                status = "WARNING: FUEL OVERHEATING"
                color = RED
            elif f_val > 75.0:
                status = "CAUTION: HIGH FUEL TEMP"
                color = YELLOW
        if metric.upper() == "SPD" and f_val > 350:
            status = "WARNING: OVERSPEED"
            color = YELLOW
        elif metric.upper() == "BRK" and f_val > 100 and f_val < 120:
            status = "WARNING: HEAVY BRAKING"
            color = YELLOW
        elif metric.upper() == "BRK" and f_val >= 120:
            status = "WARNING: EXTREME BRAKING - CHECK WEAR"
            color = YELLOW
        elif metric.upper() == "GFC" and abs(f_val) > 5.0 and abs(f_val) < 9.0:
            status = "WARNING: HIGH G-LOAD"
            color = YELLOW
        elif metric.upper() == "GFC" and abs(f_val) >= 9.0:
            status = "CRITICAL: POSSIBLE IMPACT DETECTED - NOTIFY MEDICAL"
            color = RED
        elif metric.upper() == "RPM" and f_val >= 14800:
            status = "WARNING: REDLINE - SHIFT IMMEDIATELY"
            color = YELLOW
        elif metric.upper() == "TYR" and f_val >= 115:
            status = "WARNING: TYRE OVERHEAT - REDUCE SLIDING"
            color = YELLOW
        elif metric.upper() == "TYR" and f_val <= 75:
            status = "WARNING: TYRE COLD - LOW GRIP"
            color = YELLOW
        elif metric.upper() == "ERS" and f_val <= 10:
            status = "WARNING: ERS LOW - DEPLOYMENT LIMITED"
            color = YELLOW

        if status != "NOMINAL":
            alerts_triggered += 1

        display_report = f"[{CYAN}{log_date} | {log_time}{RESET}] {driver_name} (#{driver_id}) | {metric}: {val} | STATUS: {color}{status}{RESET}{fuel_warning}{RESET}"
        log_report = f"[{log_date} | {log_time}] {driver_name} (#{driver_id}) | {metric}: {val} | STATUS: {status} | FUEL: {car['fuel'] if car else '??'}%"
    else:
        status = "INVALID_DATA_REJECTED"
        color = RED
        display_report = f"[{CYAN}{log_date} | {log_time}{RESET}] {driver_name} (#{driver_id}) | {metric}: {val} | STATUS: {color}{status}{RESET}{fuel_warning}"
        log_report = f"[{log_date} | {log_time}] {driver_name} (#{driver_id}) | {metric}: {val} | STATUS: {status} | FUEL: {car['fuel'] if car else '??'}%"

    # 3. AUTO-LOGGING (The persistent record)
    with open("williams_race_data.log", "a") as log_file:
        log_file.write(log_report + "\n")

    return display_report + fuel_warning
def handle_client(client_socket):
    """ Verifies the connection and routes data to the handler """
    while True:
        try:
            # Receive telemetry packet
            data_packet = client_socket.recv(1024).decode()
            if not data_packet:
                break

            response = handle_request(data_packet)
            client_socket.send(response.encode())
        except Exception as e:
            print(f"Link Lost: {e}")
            break

    client_socket.close()
        # TO DO: Receive data from the car
        # TO DO: Get response from handle_telemetry
        # TO DO: Send response back to the car (client)



def main():
    # TO DO: Initialize server socket (AF_INET, SOCK_STREAM)
    # TO DO: Bind to HOST and PORT
    # TO DO: Listen for incoming car links

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Williams Pit Wall Server: Listening on {HOST}:{PORT}")
    print(f"{W_BLUE}{BOLD}--- WILLIAMS PIT WALL SERVER ONLINE ---{RESET}")
    print(f"EVENT:   {current_track}")
    print(f"SESSION: {current_session}")
    print(f"WEATHER: {current_condition} ({track_temp}°C)")
    print(f"----------------------------------------")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Car Link Established: {client_address}")
        handle_client(client_socket)





if __name__ == "__main__":
    main()