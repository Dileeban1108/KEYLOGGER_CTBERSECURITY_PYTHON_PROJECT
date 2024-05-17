import getpass
import os
import platform
import socket
import psutil
import tkinter as tk

class SystemInfoRecorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.update_idletasks()
        self.root.update()

    def get_username(self):
        return getpass.getuser()

    def get_home_directory(self):
        return os.path.expanduser("~")

    def get_system_info(self):
        return platform.uname()

    def get_current_directory(self):
        return os.getcwd()

    def get_user_profile(self):
        return os.getenv("USERPROFILE")  # Windows

    def get_user_home(self):
        return os.getenv("HOME")  # Unix-like systems

    def get_user_name(self):
        return os.getenv("USERNAME")  # Windows

    def get_host_name(self):
        return socket.gethostname()

    def get_hardware_details(self):
        processor = platform.processor()
        virtual_memory = psutil.virtual_memory()
        total_memory = virtual_memory.total / 1024 ** 3
        available_memory = virtual_memory.available / 1024 ** 3
        return processor, total_memory, available_memory

    def get_disk_partitions(self):
        return psutil.disk_partitions()

    def write_system_info_to_file(self):
        logs_dir = os.path.join(os.getcwd(), 'system_info')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        system_info_file_path = os.path.join(logs_dir, 'system_info.txt')
        with open(system_info_file_path, "w") as file:
            file.write(f"Username: {self.get_username()}\n")
            file.write(f"Home Directory: {self.get_home_directory()}\n")
            file.write(f"System Information: {self.get_system_info()}\n")
            file.write(f"Current Working Directory: {self.get_current_directory()}\n")
            file.write(f"User Profile: {self.get_user_profile()}\n")
            file.write(f"User Home: {self.get_user_home()}\n")
            file.write(f"User Name: {self.get_user_name()}\n")
            file.write(f"Host Name: {self.get_host_name()}\n")
            file.write("\n")
            file.write(f"System Hardware\n")
            processor, total_memory, available_memory = self.get_hardware_details()
            file.write(f" Processor: {processor}\n")
            file.write(f" Total Memory: {total_memory:.2f} GB\n")
            file.write(f" Available Memory: {available_memory:.2f} GB\n")

            file.write("\nDisk Information:\n")
            for partition in self.get_disk_partitions():
                try:
                    partition_info = psutil.disk_usage(partition.mountpoint)
                    total_size_gb = partition_info.total / 1024 ** 3
                    used_space_gb = partition_info.used / 1024 ** 3
                    free_space_gb = partition_info.free / 1024 ** 3
                    file.write(f" Partition: {partition.device}\n")
                    file.write(f"   Mountpoint: {partition.mountpoint}\n")
                    file.write(f"   Total Size: {total_size_gb:.2f} GB\n")
                    file.write(f"   Used Space: {used_space_gb:.2f} GB\n")
                    file.write(f"   Free Space: {free_space_gb:.2f} GB\n")
                    file.write(f"   Usage Percentage: {partition_info.percent}%\n\n")
                except PermissionError:
                    file.write(f"Partition: {partition.device} - Not accessible\n\n")
                    continue

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            screen_resolution = self.root.winfo_fpixels('1i')  # Pixels per inch
            file.write(f"\nScreen Information:\n")
            file.write(f" Screen Size: {screen_width} x {screen_height} pixels\n")
            file.write(f" Screen Resolution: {screen_resolution:.2f} DPI\n")

        print(f"System information written to {system_info_file_path}")

if __name__ == "__main__":
    system_info_recorder = SystemInfoRecorder()
    system_info_recorder.write_system_info_to_file()
