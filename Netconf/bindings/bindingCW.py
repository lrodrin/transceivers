# -*- coding: utf-8 -*-
from operator import attrgetter
from pyangbind.lib.yangtypes import RestrictedPrecisionDecimalType
from pyangbind.lib.yangtypes import RestrictedClassType
from pyangbind.lib.yangtypes import TypedListType
from pyangbind.lib.yangtypes import YANGBool
from pyangbind.lib.yangtypes import YANGListType
from pyangbind.lib.yangtypes import YANGDynClass
from pyangbind.lib.yangtypes import ReferenceType
from pyangbind.lib.base import PybindBase
from collections import OrderedDict
from decimal import Decimal
from bitarray import bitarray
import six

# PY3 support of some PY2 keywords (needs improved)
if six.PY3:
  import builtins as __builtin__
  long = int
elif six.PY2:
  import __builtin__

class yc_transceiver_node_connectivity__connection_transceiver(PybindBase):
  """
  This class was auto-generated by the PythonClass plugin for PYANG
  from YANG module node-connectivity - based on the path /connection/transceiver. Each member element of
  the container is represented as a class variable - with a specific
  YANG type.
  """
  __slots__ = ('_path_helper', '_extmethods', '__transceiverid',)

  _yang_name = 'transceiver'
  _yang_namespace = 'urn:node-connectivity'

  _pybind_generated_by = 'container'

  def __init__(self, *args, **kwargs):

    self._path_helper = False

    self._extmethods = False
    self.__transceiverid = YANGDynClass(base=six.text_type, is_leaf=True, yang_name="transceiverid", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, is_keyval=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)

    load = kwargs.pop("load", None)
    if args:
      if len(args) > 1:
        raise TypeError("cannot create a YANG container with >1 argument")
      all_attr = True
      for e in self._pyangbind_elements:
        if not hasattr(args[0], e):
          all_attr = False
          break
      if not all_attr:
        raise ValueError("Supplied object did not have the correct attributes")
      for e in self._pyangbind_elements:
        nobj = getattr(args[0], e)
        if nobj._changed() is False:
          continue
        setmethod = getattr(self, "_set_%s" % e)
        if load is None:
          setmethod(getattr(args[0], e))
        else:
          setmethod(getattr(args[0], e), load=load)

  def _path(self):
    if hasattr(self, "_parent"):
      return self._parent._path()+[self._yang_name]
    else:
      return ['connection', 'transceiver']

  def _get_transceiverid(self):
    """
    Getter method for transceiverid, mapped from YANG variable /connection/transceiver/transceiverid (string)
    """
    return self.__transceiverid
      
  def _set_transceiverid(self, v, load=False):
    """
    Setter method for transceiverid, mapped from YANG variable /connection/transceiver/transceiverid (string)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_transceiverid is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_transceiverid() directly.
    """
    parent = getattr(self, "_parent", None)
    if parent is not None and load is False:
      raise AttributeError("Cannot set keys directly when" +
                             " within an instantiated list")

    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=six.text_type, is_leaf=True, yang_name="transceiverid", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, is_keyval=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """transceiverid must be of a type compatible with string""",
          'defined-type': "string",
          'generated-type': """YANGDynClass(base=six.text_type, is_leaf=True, yang_name="transceiverid", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, is_keyval=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)""",
        })

    self.__transceiverid = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_transceiverid(self):
    self.__transceiverid = YANGDynClass(base=six.text_type, is_leaf=True, yang_name="transceiverid", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, is_keyval=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)

  transceiverid = __builtin__.property(_get_transceiverid, _set_transceiverid)


  _pyangbind_elements = OrderedDict([('transceiverid', transceiverid), ])


class yc_connection_node_connectivity__connection(PybindBase):
  """
  This class was auto-generated by the PythonClass plugin for PYANG
  from YANG module node-connectivity - based on the path /connection. Each member element of
  the container is represented as a class variable - with a specific
  YANG type.
  """
  __slots__ = ('_path_helper', '_extmethods', '__connectionid','__port_in_id','__port_out_out','__wavelength','__transceiver',)

  _yang_name = 'connection'
  _yang_namespace = 'urn:node-connectivity'

  _pybind_generated_by = 'container'

  def __init__(self, *args, **kwargs):

    self._path_helper = False

    self._extmethods = False
    self.__connectionid = YANGDynClass(base=six.text_type, is_leaf=True, yang_name="connectionid", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, is_keyval=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)
    self.__wavelength = YANGDynClass(base=six.text_type, is_leaf=True, yang_name="wavelength", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)
    self.__transceiver = YANGDynClass(base=YANGListType("transceiverid",yc_transceiver_node_connectivity__connection_transceiver, yang_name="transceiver", parent=self, is_container='list', user_ordered=False, path_helper=self._path_helper, yang_keys='transceiverid', extensions=None), is_container='list', yang_name="transceiver", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='list', is_config=True)
    self.__port_out_out = YANGDynClass(base=six.text_type, is_leaf=True, yang_name="port-out_out", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)
    self.__port_in_id = YANGDynClass(base=six.text_type, is_leaf=True, yang_name="port-in_id", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)

    load = kwargs.pop("load", None)
    if args:
      if len(args) > 1:
        raise TypeError("cannot create a YANG container with >1 argument")
      all_attr = True
      for e in self._pyangbind_elements:
        if not hasattr(args[0], e):
          all_attr = False
          break
      if not all_attr:
        raise ValueError("Supplied object did not have the correct attributes")
      for e in self._pyangbind_elements:
        nobj = getattr(args[0], e)
        if nobj._changed() is False:
          continue
        setmethod = getattr(self, "_set_%s" % e)
        if load is None:
          setmethod(getattr(args[0], e))
        else:
          setmethod(getattr(args[0], e), load=load)

  def _path(self):
    if hasattr(self, "_parent"):
      return self._parent._path()+[self._yang_name]
    else:
      return ['connection']

  def _get_connectionid(self):
    """
    Getter method for connectionid, mapped from YANG variable /connection/connectionid (string)
    """
    return self.__connectionid
      
  def _set_connectionid(self, v, load=False):
    """
    Setter method for connectionid, mapped from YANG variable /connection/connectionid (string)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_connectionid is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_connectionid() directly.
    """
    parent = getattr(self, "_parent", None)
    if parent is not None and load is False:
      raise AttributeError("Cannot set keys directly when" +
                             " within an instantiated list")

    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=six.text_type, is_leaf=True, yang_name="connectionid", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, is_keyval=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """connectionid must be of a type compatible with string""",
          'defined-type': "string",
          'generated-type': """YANGDynClass(base=six.text_type, is_leaf=True, yang_name="connectionid", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, is_keyval=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)""",
        })

    self.__connectionid = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_connectionid(self):
    self.__connectionid = YANGDynClass(base=six.text_type, is_leaf=True, yang_name="connectionid", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, is_keyval=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)


  def _get_port_in_id(self):
    """
    Getter method for port_in_id, mapped from YANG variable /connection/port_in_id (string)
    """
    return self.__port_in_id
      
  def _set_port_in_id(self, v, load=False):
    """
    Setter method for port_in_id, mapped from YANG variable /connection/port_in_id (string)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_port_in_id is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_port_in_id() directly.
    """
    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=six.text_type, is_leaf=True, yang_name="port-in_id", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """port_in_id must be of a type compatible with string""",
          'defined-type': "string",
          'generated-type': """YANGDynClass(base=six.text_type, is_leaf=True, yang_name="port-in_id", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)""",
        })

    self.__port_in_id = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_port_in_id(self):
    self.__port_in_id = YANGDynClass(base=six.text_type, is_leaf=True, yang_name="port-in_id", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)


  def _get_port_out_out(self):
    """
    Getter method for port_out_out, mapped from YANG variable /connection/port_out_out (string)
    """
    return self.__port_out_out
      
  def _set_port_out_out(self, v, load=False):
    """
    Setter method for port_out_out, mapped from YANG variable /connection/port_out_out (string)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_port_out_out is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_port_out_out() directly.
    """
    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=six.text_type, is_leaf=True, yang_name="port-out_out", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """port_out_out must be of a type compatible with string""",
          'defined-type': "string",
          'generated-type': """YANGDynClass(base=six.text_type, is_leaf=True, yang_name="port-out_out", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)""",
        })

    self.__port_out_out = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_port_out_out(self):
    self.__port_out_out = YANGDynClass(base=six.text_type, is_leaf=True, yang_name="port-out_out", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)


  def _get_wavelength(self):
    """
    Getter method for wavelength, mapped from YANG variable /connection/wavelength (string)
    """
    return self.__wavelength
      
  def _set_wavelength(self, v, load=False):
    """
    Setter method for wavelength, mapped from YANG variable /connection/wavelength (string)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_wavelength is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_wavelength() directly.
    """
    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=six.text_type, is_leaf=True, yang_name="wavelength", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """wavelength must be of a type compatible with string""",
          'defined-type': "string",
          'generated-type': """YANGDynClass(base=six.text_type, is_leaf=True, yang_name="wavelength", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)""",
        })

    self.__wavelength = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_wavelength(self):
    self.__wavelength = YANGDynClass(base=six.text_type, is_leaf=True, yang_name="wavelength", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='string', is_config=True)


  def _get_transceiver(self):
    """
    Getter method for transceiver, mapped from YANG variable /connection/transceiver (list)
    """
    return self.__transceiver
      
  def _set_transceiver(self, v, load=False):
    """
    Setter method for transceiver, mapped from YANG variable /connection/transceiver (list)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_transceiver is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_transceiver() directly.
    """
    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=YANGListType("transceiverid",yc_transceiver_node_connectivity__connection_transceiver, yang_name="transceiver", parent=self, is_container='list', user_ordered=False, path_helper=self._path_helper, yang_keys='transceiverid', extensions=None), is_container='list', yang_name="transceiver", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='list', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """transceiver must be of a type compatible with list""",
          'defined-type': "list",
          'generated-type': """YANGDynClass(base=YANGListType("transceiverid",yc_transceiver_node_connectivity__connection_transceiver, yang_name="transceiver", parent=self, is_container='list', user_ordered=False, path_helper=self._path_helper, yang_keys='transceiverid', extensions=None), is_container='list', yang_name="transceiver", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='list', is_config=True)""",
        })

    self.__transceiver = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_transceiver(self):
    self.__transceiver = YANGDynClass(base=YANGListType("transceiverid",yc_transceiver_node_connectivity__connection_transceiver, yang_name="transceiver", parent=self, is_container='list', user_ordered=False, path_helper=self._path_helper, yang_keys='transceiverid', extensions=None), is_container='list', yang_name="transceiver", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='list', is_config=True)

  connectionid = __builtin__.property(_get_connectionid, _set_connectionid)
  port_in_id = __builtin__.property(_get_port_in_id, _set_port_in_id)
  port_out_out = __builtin__.property(_get_port_out_out, _set_port_out_out)
  wavelength = __builtin__.property(_get_wavelength, _set_wavelength)
  transceiver = __builtin__.property(_get_transceiver, _set_transceiver)


  _pyangbind_elements = OrderedDict([('connectionid', connectionid), ('port_in_id', port_in_id), ('port_out_out', port_out_out), ('wavelength', wavelength), ('transceiver', transceiver), ])


class node_connectivity(PybindBase):
  """
  This class was auto-generated by the PythonClass plugin for PYANG
  from YANG module node-connectivity - based on the path /node-connectivity. Each member element of
  the container is represented as a class variable - with a specific
  YANG type.

  YANG Description: Latest update to node connectivity SDM YANG data model.
  """
  __slots__ = ('_path_helper', '_extmethods', '__connection',)

  _yang_name = 'node-connectivity'
  _yang_namespace = 'urn:node-connectivity'

  _pybind_generated_by = 'container'

  def __init__(self, *args, **kwargs):

    self._path_helper = False

    self._extmethods = False
    self.__connection = YANGDynClass(base=YANGListType("connectionid",yc_connection_node_connectivity__connection, yang_name="connection", parent=self, is_container='list', user_ordered=False, path_helper=self._path_helper, yang_keys='connectionid', extensions=None), is_container='list', yang_name="connection", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='list', is_config=True)

    load = kwargs.pop("load", None)
    if args:
      if len(args) > 1:
        raise TypeError("cannot create a YANG container with >1 argument")
      all_attr = True
      for e in self._pyangbind_elements:
        if not hasattr(args[0], e):
          all_attr = False
          break
      if not all_attr:
        raise ValueError("Supplied object did not have the correct attributes")
      for e in self._pyangbind_elements:
        nobj = getattr(args[0], e)
        if nobj._changed() is False:
          continue
        setmethod = getattr(self, "_set_%s" % e)
        if load is None:
          setmethod(getattr(args[0], e))
        else:
          setmethod(getattr(args[0], e), load=load)

  def _path(self):
    if hasattr(self, "_parent"):
      return self._parent._path()+[self._yang_name]
    else:
      return []

  def _get_connection(self):
    """
    Getter method for connection, mapped from YANG variable /connection (list)
    """
    return self.__connection
      
  def _set_connection(self, v, load=False):
    """
    Setter method for connection, mapped from YANG variable /connection (list)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_connection is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_connection() directly.
    """
    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=YANGListType("connectionid",yc_connection_node_connectivity__connection, yang_name="connection", parent=self, is_container='list', user_ordered=False, path_helper=self._path_helper, yang_keys='connectionid', extensions=None), is_container='list', yang_name="connection", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='list', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """connection must be of a type compatible with list""",
          'defined-type': "list",
          'generated-type': """YANGDynClass(base=YANGListType("connectionid",yc_connection_node_connectivity__connection, yang_name="connection", parent=self, is_container='list', user_ordered=False, path_helper=self._path_helper, yang_keys='connectionid', extensions=None), is_container='list', yang_name="connection", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='list', is_config=True)""",
        })

    self.__connection = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_connection(self):
    self.__connection = YANGDynClass(base=YANGListType("connectionid",yc_connection_node_connectivity__connection, yang_name="connection", parent=self, is_container='list', user_ordered=False, path_helper=self._path_helper, yang_keys='connectionid', extensions=None), is_container='list', yang_name="connection", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='urn:node-connectivity', defining_module='node-connectivity', yang_type='list', is_config=True)

  connection = __builtin__.property(_get_connection, _set_connection)


  _pyangbind_elements = OrderedDict([('connection', connection), ])


