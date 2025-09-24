# TODO

- Merge code into main and then update README paths to reflect that
- Make sure `./setup-hosts.sh testbed/testbed_opulous-octorand.json` is the right testbed.

# Reproducing

## Goodput Tests

For the goodput tests, you want to use the configs in `configs/no-xdp/` and `configs/xdp/`. The following configs are important:

### Default MsQuic Tests (i.e. No XDP for client and server)

- `configs/no-xdp/dogecoin.yaml`
- `configs/no-xdp/opulous.yaml`
- This runs 20 iterations of default MsQuic vs. default MsQuic for the Dogecoin and Opulous setups.

### XDP Server Tests (i.e. AF_XDP on the server, default MsQuic on the client)

- `configs/xdp/skb/server-only/dogecoin.yaml`
- `configs/xdp/skb/server-only/opulous.yaml`
- This runs 20 iterations of AF_XDP on the server in XDP_SKB mode for the Dogecoin and Opulous setups.
- `configs/xdp/drv-no-zc/server-only/dogecoin.yaml`
- `configs/xdp/drv-no-zc/server-only/opulous.yaml`
- This runs 20 iterations of AF_XDP on the server in XDP_DRV mode _without_ zerocopy enabled for the Dogecoin and Opulous setups.
- `configs/xdp/drv-zc/server-only/dogecoin.yaml`
- `configs/xdp/drv-zc/server-only/opulous.yaml`
- This runs 20 iterations of AF_XDP on the server in XDP_DRV mode _with_ zerocopy enabled for the Dogecoin and Opulous setups.

### XDP Client Tests (i.e. default MsQuic on the server, AF_XDP on the client)

- `configs/xdp/skb/client-only/dogecoin.yaml`
- `configs/xdp/skb/client-only/opulous.yaml`
- This runs 20 iterations of AF_XDP on the client in XDP_SKB mode for the Dogecoin and Opulous setups.
- `configs/xdp/drv-no-zc/client-only/dogecoin.yaml`
- `configs/xdp/drv-no-zc/client-only/opulous.yaml`
- This runs 20 iterations of AF_XDP on the client in XDP_DRV mode _without_ zerocopy enabled for the Dogecoin and Opulous setups.
- `configs/xdp/drv-zc/client-only/dogecoin.yaml`
- `configs/xdp/drv-zc/client-only/opulous.yaml`
- This runs 20 iterations of AF_XDP on the client in XDP_DRV mode _with_ zerocopy enabled for the Dogecoin and Opulous setups.

### XDP Batch Size Tests (i.e. default MsQuic on the server, AF_XDP on the client with different batch sizes)

- `configs/xdp/drv-zc/client-only/batch-sizes/dogecoin-batch-1.yaml`
- `configs/xdp/drv-zc/client-only/batch-sizes/dogecoin-batch-2.yaml`
- `configs/xdp/drv-zc/client-only/batch-sizes/dogecoin-batch-4.yaml`
- `configs/xdp/drv-zc/client-only/batch-sizes/dogecoin-batch-8.yaml`
- `configs/xdp/drv-zc/client-only/batch-sizes/dogecoin-batch-16.yaml`
- `configs/xdp/drv-zc/client-only/batch-sizes/dogecoin-batch-32.yaml`
- `configs/xdp/drv-zc/client-only/batch-sizes/dogecoin-batch-64.yaml`
- `configs/xdp/drv-zc/client-only/batch-sizes/dogecoin-batch-128.yaml`
- These configs run 20 iterations of AF_XDP on the client in XDP_DRV mode _with_ zerocopy enabled using different batch sizes for the Dogecoin setup.

### Running the goodput test

`git clone --branch 'ddritzenhoff/msquic-xdp' https://gitlab.lrz.de/netintum/projects/quic/quic-interop-runner.git`

`cd quic-interop-runner`

<!-- Create virtual environment -->
`python3 -m venv .venv`

<!-- Vim into ./venv/pyvenv.cfg and change include-system-site-packages from false to true -->
`vim .venv/pyvenv.cfg`

<!-- Start the virtual environment -->
`source .venv/bin/activate`

<!-- Install the required packages -->
`pip install -r requirements.txt`

<!-- Fetch the artifact from the MsQuic implementation -->
#### Goodput-related Artifacts

- `msquic-no-xdp`
- `msquic-xdp-skb`
- `msquic-xdp-drv-no-zc`
- `msquic-xdp-drv-zc`
- `msquic-xdp-drv-zc-batch-1`
- `msquic-xdp-drv-zc-batch-2`
- `msquic-xdp-drv-zc-batch-4`
- `msquic-xdp-drv-zc-batch-8`
- `msquic-xdp-drv-zc-batch-16`
- `msquic-xdp-drv-zc-batch-32`
- `msquic-xdp-drv-zc-batch-64`
- `msquic-xdp-drv-zc-batch-128`

`python3 fetch_artifacts.py --implementations <artifact>`

<!-- Set up the hosts -->

#### Hosts

- `./setup-hosts.sh testbed/testbed_dogecoin-dogecoincash-10GB.json`
- `./setup-hosts.sh testbed/testbed_opulous-octorand.json`

<!-- `python3 run.py --manual-mode --debug --config <config>` -->
`python3 run.py --debug --config <config>`

#### Analyzing the goodput results

- `pip install -r goodput/requirements.txt`
- Note that the goodput directory is within this repository at the top level!
- The structure of the directory mimics that of the structure of the config directory for the most part.

##### Batch Size

- Go into `batch-size/graph.py` and update the following values after you've run all the batch size tests.

```json
# Data
data = {
    '1': 1.83,
    '2': 2.29,
    '4': 2.65,
    '8': 2.98,
    '16': 3.26,
    '32': 3.48,
    '64': 3.56,
    '128': 3.54
}

# Error values for each datapath
errors = {
    '1': .060,
    '2': .101,
    '4': .103,
    '8': .176,
    '16': .188,
    '32': .182,
    '64': .185,
    '128': .137
}
```

- Generate the graph with `python3 goodput/dogecoin/batch-size/graph.py

##### Client-only

- Go into `client-only/graph.py` and update the following values after you've run all the client-only tests.

```json
data = {
    'default-GSO/GRO': 2.46,
    'default': 4.11,
    'XDP_SKB': 3.65,
    'XDP_DRV': 3.40,
    'XDP_DRV+zc': 3.5
}

# Error values for each datapath
errors = {
    'default-GSO/GRO': 0.130,
    'default': 0.207,
    'XDP_SKB': 0.620,
    'XDP_DRV': 0.267,
    'XDP_DRV+zc': 0.161
}
```

- Generate the graph with `python3 goodput/dogecoin/client-only/graph.py`
- Do the same thing for opulous after you've run the relevant client-only tests and generate the graph with `python3 goodput/opulous/client-only/graph.py`

##### Server-only

- Go into `server-only/graph.py` and update the following values after you've run all the server-only tests.

```json
# Data
data = {
    'default-GSO/GRO': 1.69,
    'default': 4.11,
    'XDP_SKB': 2.16,
    'XDP_DRV': 2.07,
    'XDP_DRV+zc': 3.03,
}

# Error values for each datapath
errors = {
    'default-GSO/GRO': .052,
    'default': 0.207,
    'XDP_SKB': 0.086,
    'XDP_DRV': 0.098,
    'XDP_DRV+zc': 0.087,
}
```

- Generate the graph with `python3 goodput/dogecoin/server-only/graph.py`
- Do the same thing for opulous after you've run the relevant client-only tests and generate the graph with `python3 goodput/opulous/client-only/graph.py`

## PTP

For the PTP tests, you want to use the configs in `configs/splitter/ptp/`. The following configs are important:

- `configs/splitter/ptp/dogecoin-no-xdp-log`
- This config runs 1 iteration of a 128 MB file with the packet reception times being logged within userspace on the client using the lttng library. No AF_XDP is used, just default MsQuic. The hardware arrival times of the packet is correspondingly logged on the sniffer. The Dogecoin setup is used.
- `configs/splitter/ptp/dogecoin-xdp-log.yaml`
- This config runs 1 iteration of a 128 MB file with the packet reception times being logged within userspace on the client using the lttng library. AF_XDP is used on the client. The hardware arrival times of the packet is correspondingly logged on the sniffer. The Dogecoin setup is used.

### Running the PTP test

`git clone --branch 'ddritzenhoff/msquic-xdp' https://gitlab.lrz.de/netintum/projects/quic/quic-interop-runner.git`

`cd quic-interop-runner`

<!-- Create virtual environment -->
`python3 -m venv .venv`

<!-- Vim into ./venv/pyvenv.cfg and change include-system-site-packages from false to true -->
`vim .venv/pyvenv.cfg`

<!-- Start the virtual environment -->
`source .venv/bin/activate`

<!-- Install the required packages -->
`pip install -r requirements.txt`

#### Make sure you have these pre and post run scripts

- `pre-post-scripts/start-ptp-tcpdump.sh`
- `pre-post-scripts/stop-ptp-tcpdump.sh`

<!-- Fetch the artifact from the MsQuic implementation -->
#### PTP-related Artifacts

- `msquic-no-xdp-log`
- `msquic-xdp-log`

`python3 fetch_artifacts.py --implementations <artifact>`

<!-- Set up the hosts -->

#### PTP-related Hosts

- `./setup-hosts.sh testbed/testbed/testbed_dogecoin-dogecoincash-10GB-splitter.json -ptp`
- The `-ptp` flag essentially copies all the files within the `ptp` directory into the client and sniffer. Then a script is invoked that compiles and installs the ptp-related code (i.e. `ptp4l` and `phc2sys`). One script is then run to ensure that the systems times are synced with the HW clock times, and another is run to ensure the hardware clock times are synced among themselves. I recommend sshing into the client and server and running these scripts yourselves as an additional sanity check.

<!-- `python3 run.py --manual-mode --debug --config <config>` -->
`python3 run.py --debug --config <config>`

### Analyzing the Results

Before going through the steps, I'd like to acknowledge that it is a janky process. I tried to iterate a few times to get it working better to no avail. However, I'm sure with more time, I could have found something. Also, when you try to reproduce, keep in mind what Stefan Lachnit said about disabling some sort of polling feature in the NIC. I wasn't aware of it until after the final presentation, which lead me to my current conclusion. For more interesting results, it may be worth to experiment with this feature. We talked about this when doing the performance review after the final presentation. Stefan said that it was a command also mentioned within one of Paul Emmerich's papers. Perhaps it was something along the lines of `ethtool -C eth0 rx-usecs <microseconds>`.

After running the test, you will find the `.json` file containing the packet numbers and their associated arrival times for the _client_ in the log directory that is generated after each completed `run.py` invocation. It'll sit in the `/client/` directory and will look something like this:

```json
{
  "date": "2025-06-25",
  "timezone": "UTC",
  "packets": [
    {
      "timestamp": "12:34:30.445071472 (UTC)",
      "fractional_part": "445071472",
      "time_part": "14:34:30",
      "epoch_time": "1750854870.445071472",
      "packet_number": 0
    },
    {
      "timestamp": "12:34:30.445414068 (UTC)",
      "fractional_part": "445414068",
      "time_part": "14:34:30",
      "epoch_time": "1750854870.445414068",
      "packet_number": 1
    },
```

Alongside the json file is a `keys.log` file. You want to take these two files in addition to the `trace-server-ptp.pcap` file within the `/sniffer/` directory and copy everything to one place.

At the high level, the objective at this point is to create a `.json` file for the sniffer, similar to the client's `.json` file, by decrypting the pcap with the `keys.log` and then running it through the `quic-analyzer.py` script. To decrypt, I used Wireshark, but I occasionally had hang-ups with it. Another tool may be more reliable. 

Once you've gotten the decrypted pcap, you run `quic-analyzer.py` on it using a command similar to this one: `python3 quic-analyzer.py -p no-xdp-log/trace-ptp.pcap -k no-xdp-log/keys.log -s 10.0.0.2 -d 10.0.0.1 -o no-xdp-log/no-xdp-nic.json`. I've included some stubs within the `/ptp/` directory within this repository for you to take a look at and see how it's done. Finally, note that you _have_ to decrypt the pcap before invoking this script. I know the source code gives the impression that it does the decryption for you, but it was a failed attempt.

At this point in time, you should have two .json files: `no-xdp-nic.json` and `no-xdp-userspace.json` or `xdp-nic.json` and `xdp-userspace.json`. Now we want to 'zip' the files together and calculate the time difference between the userspace times to the HW timestamp times. For this we use the `zipper.py` script. We invoke it using arguments similar to this: `python3 zipper.py -fu no-xdp-log/no-xdp-userspace.json -fn no-xdp-log/no-xdp-nic.json -s 50 -o no-xdp-log/no-xdp-zipped.json`. This calculates the time difference between the same packets starting from number 50 (I've found some of the earlier packets go missing for whatever reason).

Once you have `no-xdp-zipped.json` or `xdp-zipped.json`, you can create the boxplot or CDF using the `delta-boxplots.py` and `cdf-graph.py` scripts, respectively. For `delta-boxplots.py`, the arguemnts will look like `python3 delta-boxplots.py --files no-xdp-log/no-xdp-zipped.json xdp-log/xdp-zipped.json --output figure0.pdf --labels "No XDP" "XDP"`. For `cdf-graph.py`, `python3 cdf-graph.py no-xdp-log/no-xdp-zipped.json xdp-log/xdp-zipped.json --labels "No XDP" "XDP"`.
