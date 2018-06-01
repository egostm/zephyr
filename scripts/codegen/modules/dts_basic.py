#
# Copyright (c) 2018 Bobby Noelte
#
# SPDX-License-Identifier: Apache-2.0
#

##
# @file
# Code generation module for basic device tree data access.
#

##
# @brief DTS basic template.
# @defgroup codegen_modules_dts_basic DTS basic module.
# @ingroup codegen_modules
#
# Code generation module for basic device tree properties access.
#
# The module does not generate code but provides utility function to access
# device tree properties.
#
# Usage example:
# codegen.import_module('dts_basic')
#
# @{

import codegen

def _device_tree_label(s):
    # Transmute ,- to _
    s = s.replace("-", "_")
    s = s.replace(",", "_")
    s = s.replace("@", "_")
    return s.upper()

##
# @brief Get the number of activated devices of given type.
#
# @attention The SOC_[type]_CONTROLLER_COUNT key shall be defined in
#            generated_dts_board.conf.
#
# @param device_type_name Type of device controller
#                         (e.g. 'SPI', 'GPIO', 'PIN', ...)
# @return number of activated devices
#
def device_tree_controller_count(device_type_name, default="<unset>"):
    controller_count_property_name = "SOC_{}_CONTROLLER_COUNT".format(
        device_type_name)
    return codegen.device_tree_property(controller_count_property_name,
                                        default)

##
# @brief Get the device tree prefix for the device of the given type and idx.
#
# @attention The SOC_[type]_CONTROLLER_COUNT key shall be defined in
#            generated_dts_board.conf.
#
# @param device_type_name Type of device controller
#                         (e.g. 'SPI', 'GPIO', 'PIN', ...)
# @param device_index Index of device
# @return device tree prefix (e.g. ST_STM32_SPI_FIFO_4000000)
#
def device_tree_controller_prefix(device_type_name, device_index,
                                  default="<unset>"):
    controller_prefix_property_name = "SOC_{}_CONTROLLER_{}".format(
        device_type_name, device_index)
    return codegen.device_tree_property(controller_prefix_property_name,
                                        default)

##
# @brief Get device tree property value for the device of the given type
#        and idx.
#
# @attention The SOC_[type]_CONTROLLER_[idx] key shall be defined in
#            generated_dts_board.conf.
#
# @param device_type_name Type of device controller
#                         (e.g. 'SPI', 'GPIO', 'PIN', ...)
# @param device_index Index of device
# @param property_name Property name of the device tree property define
#                      (e.g. 'BASE_ADDRESS', 'LABEL', 'IRQ_0', ...)
# @return property value as given in generated_dts_board.conf
#
def device_tree_controller_property(device_type_name, device_index,
                                    property_name, default="<unset>"):
    controller_prefix = device_tree_controller_prefix(device_type_name,
                                                      device_index, None)
    if controller_prefix is None:
        if default == "<unset>":
            default = \
            "Device tree property SOC_{}_CONTROLLER_{} not defined.".format(
                device_type_name, device_index)
        return default
    property_name = "{}_{}".format(controller_prefix, property_name)
    return codegen.device_tree_property(property_name, default)

##
# @brief Get the property of another device given by a property.
#
# @param device_type_name Type of device controller
#                         (e.g. 'SPI', 'GPIO', 'PIN', ...)
# @param device_index Index of device
# @param property_name Property that denotes the dts prefix of the other
#                      device
# @param property_indirect property of the other device
# @return property value of the other device
#
def device_tree_controller_property_indirect(device_type_name, device_index,
                                             property_name,
                                             property_name_indirect,
                                             default="<unset>"):
    controller_prefix = device_tree_controller_property(
        device_type_name, device_index, property_name, None)
    if controller_prefix is None:
        if default == "<unset>":
            controller_prefix = device_tree_controller_prefix(
                device_type_name, device_index)
            default = \
            "Device tree property {}_{} not defined.".format(
                controller_prefix, property_name)
        return default
    property_name = "{}_{}".format(controller_prefix, property_name_indirect)
    return codegen.device_tree_property(property_name, default)

##
# @brief Check compatibility to device given by type and idx.
#
# The @p compatible parameter is checked against the compatible property of
# the device given by @p device_type_name and @p device_index.
#
# @param device_type_name Type of device controller
#                         (e.g. 'SPI', 'GPIO', 'PIN', ...)
# @param device_index Index of device
# @param compatible driver compatibility string (e.g. st,stm32-spi-fifo)
# @return 1 if compatible, 0 otherwise
#
def device_tree_controller_compatible_x(device_type_name,
                                        device_index, compatible,
                                        default="<unset>"):
    compatible_count = device_tree_controller_property(
        device_type_name, device_index, 'COMPATIBLE_COUNT', None)
    if compatible_count is None or int(compatible_count) == 0:
        return 0
    compatible_count = int(compatible_count)
    # sanitize for label usage
    compatible = _device_tree_label(compatible)
    compatible_id_property_name = "COMPATIBLE_ID_{}".format(compatible)
    compatible_id = codegen.device_tree_property(compatible_id_property_name,
                                                 None)
    if compatible_id is None:
        if default == "<unset>":
            default = \
            "Device tree property COMPATIBLE_ID_{} not defined.".format(
                compatible)
        return default
    for x in range(0, compatible_count):
        controller_compatibe_id_property_label = "COMPATIBLE_{}_ID".format(x)
        controller_compatibe_id = device_tree_controller_property(
            device_type_name, device_index,
            controller_compatibe_id_property_label, None)
        if controller_compatibe_id == compatible_id:
            return 1
    return 0

##
# @brief Check compatibility to at least one activated device of given type.
#
# The @p compatible parameter is checked against the compatible property of
# all activated devices of given @p type.
#
# @param device_type_name Type of device controller
#                         (e.g. 'SPI', 'GPIO', 'PIN', ...)
# @param compatible driver compatibility string (e.g. 'st,stm32-spi-fifo')
# @return 1 if there is compatibility to at least one activated device,
#         0 otherwise
#
def device_tree_controller_compatible(device_type_name, compatible):
    controller_count = device_tree_controller_count(device_type_name, None)
    if controller_count is None or int(controller_count) == 0:
        return 0
    controller_count = int(controller_count)
    for x in range(0, controller_count):
        if device_tree_controller_compatible_x(
            device_type_name, x, compatible, None) == 1:
            return 1
    return 0

##
# @brief Get the name of the driver data.
#
# Generates an unique name for driver data.
#
# @attention The SOC_[type]_CONTROLLER_[idx] key shall be defined in
#            generated_dts_board.conf.
#
# @param device_type_name Type of device controller
#                         (e.g. 'SPI', 'GPIO', 'PIN', ...)
# @param device_index Index of device
# @param data suffix for data
# @return controller data name (e.g. ST_STM32_SPI_FIFO_4000000_config)
#
def device_tree_controller_data_name(device_type_name, device_index,
                                     data):
    data_name = "{}_{}".format(
        device_tree_controller_prefix(device_type_name, device_index),
        data)
    return data_name

##
# @brief Get the device name.
#
# The device tree prefix is used as the device name.
#
# @attention The SOC_[type]_CONTROLLER_[idx] key shall be defined in
#            generated_dts_board.conf.
#
# @param device_type_name Type of device controller
#                         (e.g. 'SPI', 'GPIO', 'PIN', ...)
# @param device_index Index of device
# @return device name (e.g. ST_STM32_SPI_FIFO_4000000)
#
def device_tree_controller_device_name(device_type_name,
                                       device_index):
    return device_tree_controller_prefix(device_type_name,
                                              device_index)

##
# @brief Get the driver name.
#
# This is a convenience function for:
#   - device_tree_controller_property(device_type_name, device_index,
#                                     'LABEL')
#
# @attention The SOC_[type]_CONTROLLER_[idx] key shall be defined in
#            generated_dts_board.conf.
#
# @param device_type_name Type of device controller
#                         (e.g. 'SPI', 'GPIO', 'PIN', ...)
# @param device_index Index of device
# @return driver name (e.g. "SPI_0")
#
def device_tree_controller_driver_name(device_type_name,
                                       device_index):
    return device_tree_controller_property(device_type_name,
                                                device_index,
                                                'LABEL')

def device_tree_controller_driver_name_indirect(device_type_name,
                                                device_index, property_name):
    return device_tree_controller_property_indirect(
        device_type_name, device_index, property_name, 'LABEL')

##
# @brief Get the device index of the controller with the given name.
#
# @param device_type_name Type of device controller
#                         (e.g. 'SPI', 'GPIO', 'PIN', ...)
# @param driver_name driver name (e.g. 'SPI_1')
# @return Index of device if found or None
#
def device_tree_controller_device_index(device_type_name, driver_name):
    count = device_tree_controller_count(device_type_name, None)
    if count is None:
        return None
    for x in range(0, int(count)):
        name = device_tree_controller_driver_name(device_type_name, x)
        if name == driver_name:
               return x
    return None

def if_device_tree_controller_compatible(device_type_name, compatible):
    is_compatible = device_tree_controller_compatible(device_type_name,
                                                      compatible)
    codegen.outl("// Guard({}) {}-controller {}".format(
        is_compatible, device_type_name.lower(), compatible))
    if not is_compatible:
        codegen.stop_code_generation()

def outl_guard_device_tree_controller(device_type_name, compatible):
    is_compatible = device_tree_controller_compatible(device_type_name,
                                                      compatible)
    codegen.outl("#if {} // Guard({}) {}-controller {}".format(
        is_compatible, is_compatible, device_type_name.lower(), compatible))

def outl_unguard_device_tree_controller(device_type_name, compatible):
    is_compatible = device_tree_controller_compatible(device_type_name,
                                                      compatible)
    codegen.outl("#endif // Guard({}) {}-controller {}".format(
        is_compatible, device_type_name.lower(), compatible))

## @}
