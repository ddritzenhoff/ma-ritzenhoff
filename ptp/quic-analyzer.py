import pyshark
import json
import os
from datetime import datetime, timezone
import argparse # Import argparse for command-line arguments

def decrypt_and_extract_quic_data(pcap_file, keylog_file, source_ip, dest_ip, output_json_file, packet_limit=None, tshark_path=None):
    """
    Decrypts QUIC packets from a pcap file using a SSLKEYLOGFILE,
    filters by source and destination IP, and extracts packet number
    and epoch arrival time into a JSON file. The timestamps in the
    output will be in UTC to avoid adding any hours.

    Args:
        pcap_file (str): Path to the input .pcap file.
        keylog_file (str): Path to the SSLKEYLOGFILE for TLS decryption.
        source_ip (str): Source IP address to filter packets.
        dest_ip (str): Destination IP address to filter packets.
        output_json_file (str): Path to the output JSON file.
        packet_limit (int, optional): The maximum number of packets to process.
                                      If None, all packets will be processed.
        tshark_path (str, optional): Explicit path to the tshark executable.
                                     If None, pyshark will try to find it.
    """
    if not os.path.exists(pcap_file):
        print(f"Error: PCAP file not found at '{pcap_file}'")
        return
    if not os.path.exists(keylog_file):
        print(f"Error: SSLKEYLOGFILE not found at '{keylog_file}')")
        print("Please ensure you have generated this file when the QUIC connection was made.")
        return

    # Set the SSLKEYLOGFILE environment variable for TShark
    os.environ['SSLKEYLOGFILE'] = keylog_file
    print(f"Set SSLKEYLOGFILE environment variable to: {os.environ['SSLKEYLOGFILE']}")

    # Optionally set TShark path if provided via flag
    if tshark_path:
        try:
            pyshark.tshark.tshark.config.set_tshark_path(tshark_path)
            print(f"Set TShark executable path to: {tshark_path}")
        except Exception as e:
            print(f"Warning: Could not set TShark path to '{tshark_path}'. Pyshark will try to find it automatically. Error: {e}")
    
    # Debug print for SSLKEYLOGFILE before capture
    print(f"DEBUG: SSLKEYLOGFILE before capture: {os.environ.get('SSLKEYLOGFILE')}")


    packets_data = []
    first_packet_sniff_time = None # This will now store a UTC datetime object from sniff_timestamp

    display_filter = f"quic && ip.src eq {source_ip} && ip.dst eq {dest_ip}"
    print(f"Starting capture with filter: '{display_filter}' on '{pcap_file}'...")
    if packet_limit is not None:
        print(f"Processing a maximum of {packet_limit} packets.")
    else:
        print("Processing all matching packets.")

    try:
        cap = pyshark.FileCapture(
            input_file=pcap_file,
            display_filter=display_filter,
            decode_as={'udp.port==4433': 'quic'},
            only_summaries=False
        )

        for i, packet in enumerate(cap):
            # Check for packet limit
            if packet_limit is not None and i >= packet_limit:
                print(f"Packet limit ({packet_limit}) reached. Stopping processing.")
                break

            if hasattr(packet, 'quic') and hasattr(packet.quic, 'packet_number'):
                try:
                    # Get the original sniff_timestamp string from pyshark
                    original_sniff_timestamp_str = packet.sniff_timestamp
                    
                    # Define the TAI-UTC offset
                    TAI_UTC_OFFSET_SECONDS = 37  # as of June 2025 (verify this for your specific capture period)

                    # Split the timestamp string into seconds and fractional parts
                    parts = original_sniff_timestamp_str.split('.')
                    
                    # Convert the integer seconds part to an integer
                    original_seconds_int = int(parts[0])
                    
                    # The fractional part (string) retains its full precision
                    original_fractional_str = parts[1] if len(parts) > 1 else "0"

                    # Apply the offset ONLY to the integer seconds part
                    adjusted_seconds_int = original_seconds_int - TAI_UTC_OFFSET_SECONDS

                    # Reconstruct the adjusted epoch time as a string for precise formatting
                    adjusted_epoch_time_str = f"{adjusted_seconds_int}.{original_fractional_str}"
                    
                    # Convert the adjusted epoch time string back to float for datetime object creation
                    # Note: datetime.fromtimestamp internally converts to float, which might
                    # still introduce minuscule inaccuracies beyond microseconds, but the primary
                    # epoch_time_str_formatted will use the string representation.
                    adjusted_epoch_time_float_for_dt = float(adjusted_epoch_time_str)

                    # Convert the adjusted epoch_time_float_for_dt to a UTC datetime object for the HH:MM:SS part
                    timestamp_dt_utc = datetime.fromtimestamp(adjusted_epoch_time_float_for_dt, tz=timezone.utc)
                    
                    # Keep track of the first packet's timestamp (now UTC-aware) for timezone string
                    if first_packet_sniff_time is None:
                        first_packet_sniff_time = timestamp_dt_utc

                    # Construct the formatted_timestamp to have full nanosecond precision
                    # Take HH:MM:SS from the UTC datetime object
                    hms_part = timestamp_dt_utc.strftime('%H:%M:%S')
                    
                    # The fractional part directly from the original Pyshark string
                    # This ensures the highest precision in the fractional component.
                    # We ensure it's padded to 9 digits if it's shorter, or truncated if longer than needed for display.
                    # Given 'sniff_timestamp' is often nano, 9 digits is usually desired.
                    fractional_part_display = original_fractional_str.ljust(9, '0')[:9]
                    
                    formatted_timestamp = f"{hms_part}.{fractional_part_display}"
                    
                    packet_info = {
                        "timestamp": formatted_timestamp, # UTC with precise fractional part
                        "epoch_time": adjusted_epoch_time_str, # The precisely adjusted UTC epoch string
                        "fractional_part": original_fractional_str, # Renamed for clarity from 'parts[1]'
                        "packet_number": int(packet.quic.packet_number)
                    }
                    packets_data.append(packet_info)

                except AttributeError as e:
                    print(f"Warning: Could not extract all QUIC info from packet {i+1}: {e}")
                except (ValueError, IndexError) as e: # Add IndexError for split() issues
                    print(f"Warning: Data conversion/parsing error for packet {i+1}: {e}. Original timestamp: '{original_sniff_timestamp_str}'")
            
            # Print progress
            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1} packets...")

        cap.close()

        if not packets_data:
            print("No matching decrypted QUIC packets found.")
            return

        # Determine timezone offset for the JSON header based on UTC
        timezone_str = "+0000" # Explicitly set to UTC offset

        # Using the date of the first packet for metadata date, if available, otherwise current date
        if first_packet_sniff_time:
            # We explicitly chose UTC for timestamps, so the metadata date should reflect that.
            date_for_metadata = first_packet_sniff_time.strftime('%Y-%m-%d')
        else:
            date_for_metadata = datetime.now(timezone.utc).strftime('%Y-%m-%d')


        result_json = {
            "date": date_for_metadata,
            "timezone": timezone_str, # This will be "+0000" indicating UTC
            "packets": packets_data
        }

        with open(output_json_file, 'w') as f:
            json.dump(result_json, f, indent=2)

        print(f"\nSuccessfully extracted data and saved to '{output_json_file}' containing {len(packets_data)} packets.")

    except pyshark.capture.capture.TSharkCrashException as e:
        print(f"Error: TShark crashed. Please check your Wireshark/TShark installation and ensure the SSLKEYLOGFILE is correct and the pcap is not corrupted.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'SSLKEYLOGFILE' in os.environ:
            del os.environ['SSLKEYLOGFILE']
        print("SSLKEYLOGFILE environment variable cleared.")


# --- Main execution block ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Decrypt QUIC packets from a PCAP using SSLKEYLOGFILE and extract data to JSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Shows default values in help
    )

    parser.add_argument('-p', '--pcap-file', required=True, 
                        help="Path to the input .pcap file.")
    parser.add_argument('-k', '--keylog-file', required=True, 
                        help="Path to the SSLKEYLOGFILE for TLS decryption.")
    parser.add_argument('-s', '--source-ip', required=True, 
                        help="Source IP address to filter packets (e.g., '10.0.0.2').")
    parser.add_argument('-d', '--dest-ip', required=True, 
                        help="Destination IP address to filter packets (e.g., '10.0.0.1').")
    parser.add_argument('-o', '--output-file', required=True, 
                        help="Path for the output JSON file.")
    parser.add_argument('-l', '--limit', type=int, default=None, 
                        help="Optional: Maximum number of packets to process. If not specified, all matching packets will be processed.")
    parser.add_argument('-t', '--tshark-path', type=str, default=None,
                        help="Optional: Explicit path to the TShark executable (e.g., '/usr/bin/tshark' or 'C:\\Program Files\\Wireshark\\tshark.exe').")

    args = parser.parse_args()

    # Call the main function with arguments from the parser
    decrypt_and_extract_quic_data(
        pcap_file=args.pcap_file,
        keylog_file=args.keylog_file,
        source_ip=args.source_ip,
        dest_ip=args.dest_ip,
        output_json_file=args.output_file,
        packet_limit=args.limit,
        tshark_path=args.tshark_path # Pass the optional tshark path
    )

# python3 quic-analyzer.py -p no-xdp-no-gro-log/trace-ptp.pcap -k no-xdp-no-gro-log/keys.log -s 10.0.0.2 -d 10.0.0.1 -o no-xdp-no-gro-log/xdp-nic.json