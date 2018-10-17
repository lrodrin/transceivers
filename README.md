# restAPI
## Getting Started <a name="getting-started"></a>

**PyangBind** installation:

```
$ git clone https://github.com/robshakir/pyangbind.git
$ cd pyangbind/
$ python setup.py install
```

### Generating a Set of Classes <a name="generating-classes"></a>

To generate a set of Python classes, Pyang needs to be provided a pointer to where PyangBind's plugin is installed. This location can be found by running:

```
$ export PYBINDPLUGIN=`/usr/bin/env python -c \
'import pyangbind; import os; print ("{}/plugin".format(os.path.dirname(pyangbind.__file__)))'`
$ echo $PYBINDPLUGIN
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
from binding import node_topology
nt = node_topology()
```

### Using the Classes in a NETCONF Server <a name="using-in-netconf"></a>

**Netconf** installation:

```
$ pip install netconf
```
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
# TODO
```
### Using the Classes in a NETCONF client <a name="using-in-netconf"></a>

