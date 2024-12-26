import psutil 

if __name__ == "__main__":
    addrs = psutil.net_if_addrs()
    for interface in addrs:
        # print(add, addrs[add])
        print(f'interface name: {interface}')
        for add in addrs[interface]:
            print(f'{add.family}')
            print(f'{add.address}')
            print(f'{add.netmask}')
            print(f'{add.broadcast}')
            print()