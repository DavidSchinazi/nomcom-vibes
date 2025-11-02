![NomCom Vibes Logo](/static/logo.jpg)

# NomCom Vibes

This project gathers data from the [IETF datatracker](https://datatracker.ietf.org/)
and presents it in a manner optimized for NomCom consumption.

Most of the data is gathered from public API calls but the NomCom feedback
can only be accessed by using a cookie that requires NomCom access and
proof of access to the NomCom private key.

First you'll need to install derpendencies via:

```
python3 -m pip install bs4 lxml requests
```

Then you can run the tool via:

```
./bin/run.py
```
