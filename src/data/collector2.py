import psutil as psu

def cpu_info():
    cpu_percent = psu.cpu_percent(internval=1)
    # number of logical cores
    cpu_count = psu.cpu_count(loical=True)

    return {"cpu_percent": cpu_percent, "cpu_count": cpu_count}


def mem_info():
    mem = psu.virtual_memory()
    total = mem.total
    available = mem.available   
    percent = mem.percent

    used = mem.used
    free = mem.free
    wired = mem.wired


    swap = psu.swap_memory()
    s_total = swap.total
    s_used = swap.used
    s_free = swap.free
    s_percent = swap.percent
    s_in = swap.sin
    s_out = swap.sout

    return {
        "total": total, 
        "available": available, 
        "percent": percent, 
        "used": used, 
        "free": free, 
        "wired": wired, 
        "s_total": s_total, 
        "s_used": s_used, 
        "s_free": s_free, 
        "s_percent": s_percent, 
        "s_in": s_in, 
        "s_out": s_out
    }

def disk_info(disk_path='/', partition=False):
    disk_partitions = psutil.disk_partitions(partition)
    disk_usage = psutil.disk_usage(disk_path)
    disk_io_counters(True, True)
    # read_count
    # write_count
    # read_bytes
    # write_bytes
    # read_time
    # write_time

    return {"disk_partitions": disk_partitions, "disk_usage": disk_usage, "disk_io_counters": disk_io_counters}


def network_info():
    net_io_counters = psu.net_io_counters()
    
    return {"net_io_counters": net_io_counters}
def sensor_info():
    temperature = psu.sensors_temperatures()
    fans = psu.sensors_fans()
    battery = psu.sensors_battery()

    return {"temperature": temperature, "fans": fans, "battery": battery}
def process_info():
    return

def others_info():
    boot_time = psu.boot_time()
    users = psu.users()
    return {"boot_time": boot_time, "users": users}

print(mem_info())