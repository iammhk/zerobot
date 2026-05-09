# fix_shutdown.py - Disables the default OS response to the Power key
import os

def main():
    conf_path = "/etc/systemd/logind.conf"
    if not os.path.exists(conf_path):
        print(f"Error: {conf_path} not found.")
        return

    with open(conf_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    found = False
    for line in lines:
        if line.strip().startswith("HandlePowerKey="):
            new_lines.append("HandlePowerKey=ignore\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        # Check for commented version
        found_commented = False
        for i, line in enumerate(new_lines):
            if "#HandlePowerKey=" in line:
                new_lines[i] = "HandlePowerKey=ignore\n"
                found_commented = True
                break
        
        if not found_commented:
            new_lines.append("\n[Login]\nHandlePowerKey=ignore\n")

    with open(conf_path, 'w') as f:
        f.writelines(new_lines)
    
    print("Success: HandlePowerKey set to 'ignore' in /etc/systemd/logind.conf")
    print("Please run 'sudo systemctl restart systemd-logind' to apply.")

if __name__ == "__main__":
    main()
