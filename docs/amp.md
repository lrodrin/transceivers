# Amp class
The simplest class generated looks like:

```python
from lib.amp import Amp
manlight = Amp('10.1.1.15')
```
To generate the class we need the ip address of the amplifier.

### Methods
* `mode` enable / disable channel.
* `enable` enable / disable channel.
* `status` 
check mode (enable/disable) and put it into the variable 'stat'
check status (enable/disable) and put it into the variable 'stat'
* `test` just as test, ask for instrument ID according to SCPI API.