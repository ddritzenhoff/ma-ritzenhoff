import json
import os
import argparse

def get_file_basename(file_path):
    """Extracts the filename without path and extension."""
    return os.path.splitext(os.path.basename(file_path))[0]

def load_json_data(file_path):
    """
    Loads packet data from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        tuple: A tuple containing:
               - dict: A dictionary mapping packet_number to its full packet data.
               - str: The base name of the file (without path or extension).
               Returns (None, None) if the file cannot be loaded.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return None, None
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            packets_dict = {packet['packet_number']: packet for packet in data.get('packets', [])}
            return packets_dict, get_file_basename(file_path)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'. Please check file format.")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred while loading '{file_path}': {e}")
        return None, None

def combine_and_save_quic_data(file_userspace_path, file_nic_path, output_json_file, start_packet_number=50):
    """
    Loads two JSON files, matches packets by number, calculates time deltas in nanoseconds,
    and saves the combined data into a new JSON file.

    Args:
        file_userspace_path (str): Path to the JSON file containing userspace timestamps (file1).
        file_nic_path (str): Path to the JSON file containing NIC hardware timestamps (file2).
        output_json_file (str): The filename for the combined output JSON.
        start_packet_number (int): The packet number from which to start matching.
    """
    print(f"Loading userspace data from '{file_userspace_path}'...")
    packets_userspace, name_userspace = load_json_data(file_userspace_path)
    if packets_userspace is None:
        print("Aborting due to error loading userspace file.")
        return

    print(f"Loading NIC data from '{file_nic_path}'...")
    packets_nic, name_nic = load_json_data(file_nic_path)
    if packets_nic is None:
        print("Aborting due to error loading NIC file.")
        return

    combined_packets_data = []

    # Determine the range of packet numbers to iterate over
    max_packet_number = max(max(packets_userspace.keys(), default=0), max(packets_nic.keys(), default=0))
    print(f"Max packet number found: {max_packet_number}")
    print(f"Starting combined analysis from packet number: {start_packet_number}")

    for i in range(start_packet_number, max_packet_number + 1):
        packet_userspace_data = packets_userspace.get(i)
        packet_nic_data = packets_nic.get(i)

        if packet_userspace_data and packet_nic_data:
            try:
                # Extract original timestamp and epoch_time strings
                timestamp_userspace_str = packet_userspace_data.get('timestamp', 'N/A')
                epoch_time_userspace_str = packet_userspace_data.get('epoch_time', 'N/A')
                
                timestamp_nic_str = packet_nic_data.get('timestamp', 'N/A')
                epoch_time_nic_str = packet_nic_data.get('epoch_time', 'N/A')

                # --- High-precision delta calculation using integer nanoseconds ---
                # Split epoch_time strings into seconds and fractional parts
                userspace_sec_str, userspace_nano_str = epoch_time_userspace_str.split('.')
                nic_sec_str, nic_nano_str = epoch_time_nic_str.split('.')

                # Pad nanosecond strings to 9 digits and convert to integer
                # .ljust(9, '0') adds trailing zeros if shorter
                # [:9] truncates if longer than 9 digits (shouldn't happen with standard pyshark output)
                total_nanos_userspace = int(userspace_sec_str) * 1_000_000_000 + int(userspace_nano_str.ljust(9, '0')[:9])
                total_nanos_nic = int(nic_sec_str) * 1_000_000_000 + int(nic_nano_str.ljust(9, '0')[:9])

                # Calculate delta in nanoseconds (integer arithmetic)
                # Userspace time - NIC time
                delta_nanos = total_nanos_userspace - total_nanos_nic

                delta_microseconds = delta_nanos / 1000.0
                
                combined_packet_info = {
                    f"timestamp_{name_userspace}": timestamp_userspace_str,
                    f"timestamp_{name_nic}": timestamp_nic_str,
                    f"epoch_time_{name_userspace}": epoch_time_userspace_str,
                    f"epoch_time_{name_nic}": epoch_time_nic_str,
                    "delta": delta_nanos, # Delta as an integer in nanoseconds
                    "delta_microseconds": delta_microseconds,
                    "packet_number": i
                }
                combined_packets_data.append(combined_packet_info)

            except (KeyError, ValueError, IndexError) as e:
                # IndexError can occur if split('.') doesn't find a '.' or if parts are empty
                print(f"Warning: Skipping packet {i} due to missing data or parsing error for epoch_time: {e}. Raw data: userspace='{epoch_time_userspace_str}', nic='{epoch_time_nic_str}'")
        # else:
        #     print(f"Packet {i} not found in both files. Skipping.")

    if not combined_packets_data:
        print(f"No matching packets found from packet number {start_packet_number} onwards to combine.")
        return

    result_json = {
        "packets": combined_packets_data
    }

    try:
        with open(output_json_file, 'w') as f:
            json.dump(result_json, f, indent=2)
        print(f"\nSuccessfully combined data and saved to '{output_json_file}' containing {len(combined_packets_data)} matched packets.")
    except Exception as e:
        print(f"Error saving combined JSON to '{output_json_file}': {e}")


# --- Main execution block ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine two JSON packet data files and calculate time deltas in nanoseconds.")
    parser.add_argument('-fu', '--file-userspace', required=True, 
                        help="Path to the JSON file containing the userspace timestamps (this will be 'file1').")
    parser.add_argument('-fn', '--file-nic', required=True, 
                        help="Path to the JSON file containing the NIC hardware timestamps from the sniffer (this will be 'file2').")
    parser.add_argument('-o', '--output', required=True, help="Path for the output combined JSON file.")
    parser.add_argument('-s', '--start-packet', type=int, default=50, 
                        help="The packet number from which to start matching (default: 50).")

    args = parser.parse_args()

    combine_and_save_quic_data(
        file_userspace_path=args.file_userspace,
        file_nic_path=args.file_nic,
        output_json_file=args.output,
        start_packet_number=args.start_packet
    )

# python3 zipper.py -fu no-xdp-no-gro-log/xdp-userspace.json -fn no-xdp-no-gro-log/xdp-nic.json -s 50 -o no-xdp-no-gro-log/xdp-zipped.json