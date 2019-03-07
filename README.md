# restAPI
## Getting Started <a name="getting-started"></a>

**PyangBind** installation:

```
$ git clone https://github.com/robshakir/pyangbind.git
$ cd pyangbind/
$ python3 setup.py install
```

### Generating a Set of Classes <a name="generating-classes"></a>

To generate a set of Python classes, Pyang needs to be provided a pointer to where PyangBind's plugin is installed. This location can be found by running:

```
$ export PYBINDPLUGIN=`/usr/bin/env python3 -c \
'import pyangbind; import os; print ("{}/plugin".format(os.path.dirname(pyangbind.__file__)))'`
```

Once this path is known, it can be provided to the `--plugin-dir` argument to Pyang.

```
$ pyang --plugindir $PYBINDPLUGIN -f pybind -o binding.py node-topology.yang
```
where:

* `$PYBINDPLUGIN` is the location that was exported from the above command.
* `binding.py` is the desired output file.
* `node-topology.yang` is the YANG file that bindings are to be generated for.

The simplest class generated using a PyangBind looks like:

```python
from Netconf.bindingTopology import node_topology
nt = node_topology()
```

### Creating a Data Instance <a name="creating-data-instance"></a>

At this point, the `nt` object can be used to manipulate the YANG data tree that is expressed by the module.

A subset of `node-topology` looks like the following tree:
```
module: node-topology
    +--rw node* [node-id]
       +--rw node-id    string
       +--rw port* [port-id]
          +--rw port-id                  string
          +--rw layer-protocol-name?     string
          +--rw available-core* [core-id]
```

To add an entry to the `node` list the `add` method is used:

```python
from Netconf.bindingTopology import node_topology
nt = node_topology()
new_node = nt.node.add("10.0.2.15")
```
The `node` list is addressed exactly as per the path that it has within the YANG module.

You can find more information and examples about the generic methods used to manipulate data at: http://pynms.io/pyangbind/generic_methods/

### Serialising a Data Instance <a name="serialising-data-instance"></a>

Any PyangBind class can be serialised into any of the supported formats: **XML**, **OpenConfig** and **JSON**.

```python
from pyangbind.lib.serialise import pybindIETFXMLEncoder
# Dump the entire instance as XML 
print(pybindIETFXMLEncoder.serialise(nt))
```

This outputs the following XML structured text:

```python
#TODO
```

### Deserialising a Data Instance <a name="deserialising-data-instance"></a>

Instances can be deserialised from any of the supported serialisation formats (see above) into the classes.
```python
# Load XML into an existing class structure
import Netconf.bindingTopology as binding
from pyangbind.lib.serialise import pybindIETFXMLDecoder
print(pybindIETFXMLDecoder.decode(nt, binding, 'node-topology'))
```

This outputs the following XML structured text:

```python
#TODO
```

### Using in a NETCONF server <a name="using-netconf-server"></a>

**Netconf** installation:

```
$ pip3 install netconf
```

Running **Netconf** server:

```
$ python3 server.py -file dataset/test.xml
```

### Using in a NETCONF client <a name="using-netconf-client"></a>

Running **Netconf** client:

```
$ python3 client.py 
```

#### Example Code <a name="example-code"></a>
This worked example can be found in the `Netconf` directory.

[pyang]: https://github.com/mbj4668/pyang
[codecov]: https://codecov.io/gh/robshakir/pyangbind
[pyangbind-docs]: http://pynms.io/pyangbind/