import tkinter as tk
from tkinter import ttk
from pyModbusTCP.client import ModbusClient
from threading import Thread
import time

# Modbus client setup
c = ModbusClient(host="192.168.178.79", port=502, unit_id=255)
c.open()

registers = {
    5004: 0,
    2000: 0,
    2002: 20,
}
is_running = False
fail_safe_enabled = True

def failSafeStop():
    c.write_single_register(6000, 1)

def start_modbus_client():
    global is_running
    is_running = True
    start_time = time.time()
    while is_running and (time.time() - start_time) < 1800:
        for reg in registers:
            c.write_single_register(reg, registers[reg])
            current_value = c.read_holding_registers(reg, 1)[0]
            update_register_value_label(reg, current_value)
        if fail_safe_enabled:
            c.write_single_register(6000, 1)  # Write 1 to register 6000 every loop iteration to prevent fail-safe
        current_value_6000 = c.read_holding_registers(6000, 1)[0]
        update_register_value_label(6000, current_value_6000)
        time.sleep(20)
    failSafeStop()

def stop_modbus_client():
    global is_running
    is_running = False

def on_start():
    global modbus_thread
    registers[5004] = int(register_5004_slider.get())
    registers[2000] = int(register_2000_var.get())
    register_2000_entry.config(state='disabled')
    modbus_thread = Thread(target=start_modbus_client)
    modbus_thread.start()
    start_button.config(state='disabled')
    stop_button.config(state='normal')
    register_5004_slider.config(state='normal')
    fail_safe_button.config(state='normal')

def on_stop():
    stop_modbus_client()
    register_2000_entry.config(state='normal')
    start_button.config(state='normal')
    stop_button.config(state='disabled')
    register_5004_slider.config(state='disabled')
    fail_safe_button.config(state='disabled')

def toggle_fail_safe():
    global fail_safe_enabled
    fail_safe_enabled = not fail_safe_enabled
    if fail_safe_enabled:
        c.write_single_register(6000, 1)
        fail_safe_button.config(text="Disable Fail-safe")
    else:
        c.write_single_register(6000, 0)
        fail_safe_button.config(text="Enable Fail-safe")

def update_register_value_label(register, value):
    if register == 5004:
        register_5004_label_var.set(f"Current Register 5004 Value: {value}")
    elif register == 2000:
        register_2000_label_var.set(f"Current Register 2000 Value: {value}")
    elif register == 2002:
        register_2002_label_var.set(f"Current Register 2002 Value: {value}")
    elif register == 6000:
        register_6000_label_var.set(f"Current Register 6000 Value: {value}")

def update_register_5004_value(event):
    global registers
    registers[5004] = register_5004_slider.get()

# Create the GUI
root = tk.Tk()
root.title("Modbus Client Control")

# Register 5004
ttk.Label(root, text="Register 5004 Value:").pack(pady=5)
register_5004_slider = tk.Scale(root, from_=0, to=32, orient=tk.HORIZONTAL, command=update_register_5004_value)
register_5004_slider.pack(pady=5)
register_5004_slider.config(state='disabled')

# Register 2000
ttk.Label(root, text="Register 2000 Value:").pack(pady=5)
register_2000_var = tk.StringVar(value=str(registers[2000]))
register_2000_entry = ttk.Entry(root, textvariable=register_2000_var)
register_2000_entry.pack(pady=5)

# Start and Stop buttons
start_button = ttk.Button(root, text="Start", command=on_start)
start_button.pack(pady=5)
stop_button = ttk.Button(root, text="Stop", command=on_stop)
stop_button.pack(pady=5)
stop_button.config(state='disabled')

# Fail-safe button
fail_safe_button = ttk.Button(root, text="Disable Fail-safe", command=toggle_fail_safe)
fail_safe_button.pack(pady=5)
fail_safe_button.config(state='disabled')

# Labels for current register values
register_5004_label_var = tk.StringVar(value="Current Register 5004 Value: N/A")
register_5004_label = ttk.Label(root, textvariable=register_5004_label_var)
register_5004_label.pack(pady=10)

register_2000_label_var = tk.StringVar(value="Current Register 2000 Value: N/A")
register_2000_label = ttk.Label(root, textvariable=register_2000_label_var)
register_2000_label.pack(pady=10)

register_2002_label_var = tk.StringVar(value="Current Register 2002 Value: N/A")
register_2002_label = ttk.Label(root, textvariable=register_2002_label_var)
register_2002_label.pack(pady=10)

register_6000_label_var = tk.StringVar(value="Current Register 6000 Value: N/A")
register_6000_label = ttk.Label(root, textvariable=register_6000_label_var)
register_6000_label.pack(pady=10)

root.mainloop()

# Close the connection
c.close()
