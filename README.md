# TODO

- Merge code into main and then update README paths to reflect that
- Make sure `./setup-hosts.sh testbed/testbed_opulous-octorand.json` is the right testbed.

# Reproducing

## Goodput Tests

For the goodput tests, you want to use the configs in `configs/no-xdp/` and `configs/xdp`. The following configs are important:

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

### Running the test

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
#### Artifacts

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

## PTP
