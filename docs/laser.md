# Laser class
The simplest class generated looks like:

```python
from lib.laser import Laser
yenista = Laser()
```

### Methods
* `wavelength` define wavelength in nm.
* `power` define power in dBm.
* `enable` enable / disable channel.
* `status` check status (enable/disable) and put it into the variable 'stat'.
* `test` just as test, ask for instrument ID according to SCPI API.

### Using `wavelength` method
Necessary parameters to configure `wavelength`: channel and lambda.

Example code:
```python
# channel 3 and lambda 1550.12
yenista.wavelength(3, 1550.12)
```
### Using `power` method
Necessary parameters to configure `power`: channel and power.

Example code:
```python
# channel 3 and power 14.5
yenista.power(3, 14.5)
```
### Using `enable` method
Necessary parameters to configure `enable`: channel and status.

Example code:
```python
# channel 3 and status True
yenista.enable(3, True)
```

### Using `status` method
### Using `test` method

