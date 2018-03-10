# Copyright (c) 2018 Bobby Noelte.
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

class DeviceTreeMixin(object):
    __slots__ = []

    _device_tree = None

    def _device_tree_assure(self):
        if self._device_tree is None:
            dts_file = self.cmake_variable("GENERATED_DTS_BOARD_CONF")
            dts_file = Path(dts_file)
            if not dts_file.is_file():
                raise self._get_error_exception(
                    "Generated device tree board configuration '{}' not found/ no access.".
                    format(dts_file), 2)
            dts = {}
            with open(str(dts_file)) as dts_fd:
                for line in dts_fd:
                    if line.startswith('#'):
                        continue
                    if "=" not in line:
                        continue
                    key, value = line.partition("=")[::2]
                    dts[key.strip()] = value.strip()
            self._device_tree = dts

    ##
    # @brief Get the value of a device tree property given by the property name.
    #
    # The property name is the one in generated_dts_includes.conf.
    #
    # @param property_name property name (e.g. ST_STM32_SPI_FIFO_4000000_LABEL)
    # @param default [optional] value to be returned if property is not given.
    # @return property value
    #
    def device_tree_property(self, property_name, default="<unset>"):
        self._device_tree_assure()
        property_value = self._device_tree.get(property_name, default)
        if property_value == "<unset>":
            raise self._get_error_exception(
                "Device tree property '{}' not defined.".
                format(property_name), 1)
        return property_value

    ##
    # @brief Get all device tree properties.
    #
    # The property names are the ones in generated_dts_includes.conf.
    #
    # @return A dictionary of device tree properties.
    #
    def device_tree_properties(self):
        self._device_tree_assure()
        return self._device_tree


