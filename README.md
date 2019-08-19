 # dex

dex will index scans of exposed devices from [ipv4scan](https://github.com/wybiral/ipv4scan) and create a growing real-time database of the results. It then provides a basic regex search interface to help find specific devices.

## Getting started
This project requires the flask module for the web server. You can usually install that with:
```
pip3 install flask
```
Then you need to pipe the ipv4scan results into collect.py to start indexing:
```
ipv4scan -n 500 | python3 collect.py
```
Then start main.py to serve the web search interface:
```
python3 main.py
```
And finally navigate to http://localhost:8666 and enter your regex search queries to start looking for devices.