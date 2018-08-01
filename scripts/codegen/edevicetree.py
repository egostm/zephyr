# Copyright (c) 2018 Bobby Noelte.
# Copyright (c) 2018 Linaro Limited.
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import json
import pprint

class EDeviceTreeMixin(object):
    __slots__ = []

    _edts = None
    _compatible = None

    def _device_tree_label(s):
        # Transmute ,- to _
        s = s.replace("-", "_")
        s = s.replace(",", "_")
        s = s.replace("@", "_")
        return s.upper()

    @staticmethod
    def _device_tree_strings(s):
        # Transmute ,- to _
        s = s.replace("-", "_")
        s = s.replace(",", "_")
        s = s.replace("@", "_")
        return s

    def label_to_index(self, s):
        s = s.strip('"')
        return s.lower()

    def _edevice_tree_assure(self):
        if self._edts is None:
            dts_file = self.cmake_variable("GENERATED_DTS_BOARD_EDTS_DB", None)
            if dts_file is None:
                return \
                "CMake variable GENERATED_DTS_BOARD_EDTS_DB not defined to codegen."
            dts_file = Path(dts_file)
            if not dts_file.is_file():
                return \
                "Generated device tree board configuration {} not found/ no access.".format(dts_file)
            dts = {}
            with open(str(dts_file)) as dts_fd:
                dts = json.loads(dts_fd.read())
                self._edts = dts

    ##
    # @brief Get the compatible dict of nodes defined by board
    #
    # @return dict of compatibles defined by board
    #
    def _edevice_tree_compatibles(self):
        self._edevice_tree_assure()
        return self._edts

    ##
    # @brief Get the compatible list defined by board
    #
    # @return list of compatibles defined by board
    #
    def _edevice_tree_compatibles_list(self):
        compatibles_list = []
        compatibles = self._edevice_tree_compatibles()
        for item in compatibles:
            compatibles_list.append(item)
        return compatibles_list

    ##
    # @brief Set the compatible(s) that will be used by a driver
    #
    # These compatible will be used for driver generation
    # All compatibles will be used to find compatible nodes
    # If more than one compatible is delacred by board, the first one provided
    # by driver will be used as prefix string for driver code generation
    #
    # @return N/A
    #
    def edevice_tree_set_drivers_compatibles(self, drivers_compatibles):
        self._compatibles = []
        if not isinstance(drivers_compatibles , list):
            # TODO: check that drivers_compatible are of the same type
            drivers_compatibles = [drivers_compatibles]
        # Populate compatibles with only the compatibles declared by board
        for compat in drivers_compatibles:
            if compat in self._edevice_tree_compatibles_list():
                self._compatibles.append(compat)

    ##
    # @brief Unset compatible(s)
    #
    # @return N/A
    #
    def edevice_tree_unset_drivers_compatibles(self):
        self._compatibles = None

    ##
    # @brief Get the list of device nodes compatibles with compatible list
    #        defined by the drivers
    #
    # @return list of compatible device nodes
    #
    def edevice_tree_compatible_nodes(self):
        compatible_nodes = []
        self._edevice_tree_assure()
        drivers_compatibles = self._compatibles
        if drivers_compatibles is None:
            return "No compatible set"
        for compatible in drivers_compatibles:
            if compatible in self._edevice_tree_compatibles_list():
                # get nodes per comaptible
                for node in self._edts.get(compatible):
                    compatible_nodes.append(node)
        return compatible_nodes

    ##
    # @brief Control the driver instance generation
    #
    # @param: driver_compatibles List of compatibles supported by the driver
    #
    # @return NA
    #
    def edevice_tree_compatible_gating(self, driver_compatibles="<unset>"):
        self.generator_globals['_generate_code'] = False
        if driver_compatibles == "<unset>":
            return "Error: No compatible provided"
        self.outl("/* Guard({}) */".format(driver_compatibles))
        if not isinstance(driver_compatibles, list):
            driver_compatibles = [driver_compatibles]
        for driver_compat in driver_compatibles:
            if driver_compat in  self._edevice_tree_compatibles_list():
                self.generator_globals['_generate_code'] = True
                break


    ##
    # @brief Get the list of activated devices matching class compatible
    #
    # @return list of activated devices labels
    #
    def edevice_tree_compatible_labels(self):
        compatible_labels = []
        compatible_nodes = self.edevice_tree_compatible_nodes()
        for node in compatible_nodes:
            compatible_labels.append(node['label'])
        return compatible_labels


    ##
    # @brief Get device tree property value for the device of the given type and idx.
    #
    #
    # @param device_index Index of device
    # @param property_path Path of the property to access
    #                      (e.g. 'reg/0', 'interrupts/prio', 'label', ...)
    # @return property value as given in generated_dts_board.json
    #
    def edevice_tree_node_property(self, device_label, property_path, default="<unset>"):
        nodes = self.edevice_tree_compatible_nodes()
        for node in nodes:
            # find node with its label
            if self.label_to_index(node['label']) == device_label:
                    property_access_point = node
        property_value = property_access_point
        for key in property_path.strip("'").split('/'):
            if isinstance(property_value, list):
                if len(property_value) > 1:
                    try:
                        property_value = property_value[int(key)]
                    except ValueError:
                        pass
                else:
                    if isinstance(property_value[0], dict):
                        property_value = property_value[0]
            if isinstance(property_value, int) or isinstance(property_value, str):
                # We had what we wanted
                return property_value
            try:
                property_value = property_value[str(key)]
            except TypeError:
                property_value = property_value[int(key)]
            except KeyError:
                    # we should have a dict
                    if isinstance(property_value, dict):
                        # look for key in labels
                        try:
                            for x in range(0, len(property_value['labels'])):
                                if property_value['labels'][x] == key:
                                    property_value = property_value['data'][x]
                                    break
                        except KeyError:
                            # Looked everywhere property is not there
                            return None
                    else:
                        return "Dict was expected here"
        if property_value is None:
            if default == "<unset>":
                default = \
                "Device tree property {} not available in {}[{}]".format(property_path, compatible, device_index)
            return default
        return property_value

    ##
    # @brief Get the name of a compatible instance.
    #
    # Generates an unique name for a compatible instance. If multiple compatibles
    # were defined, use the first one
    #
    # @param device_index Index of device
    # @return instance name (e.g. st_stm32_spi_fifo_1)
    #
    def device_tree_device_instance_name(self, device_index):
        compatible_string = self._compatibles[0]
        return "{}_{}".format(self._device_tree_strings(compatible_string), device_index)

    ##
    # @brief Get the name of a driver structure.
    #
    # Generates an unique name for driver structure.
    #
    #
    # @param device_index Index of device
    # @param structure structure suffix
    # @return driver structure name (e.g. st_stm32_spi_fifo_1_data)
    #
    def device_tree_node_struct_name(self, device_index, structure):
        structure_name = "{}_{}".format(
            self.device_tree_device_instance_name(device_index),
            structure)
        return structure_name
