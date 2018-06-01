..
    Copyright (c) 2018 Bobby Noelte
    SPDX-License-Identifier: Apache-2.0

.. _codegen_modules:

Code Generation Modules
#######################

Code generation modules provide supporting functions for code generation.

.. contents::
   :depth: 2
   :local:
   :backlinks: top

Modules have to be imported to gain access to the module's functions
and variables.

 ::

    /* This file uses modules. */
    ...
    /**
     * @code{.codegen}
     * codegen.import_module('my_special_module')
     * my_special_module.do_everything():
     * @endcode{.codegen}
     */
    /** @code{.codeins}@endcode */
    ...

Basic device tree property access
*********************************

::

    codegen.import_module('dts_basic')

The module provides utility functions to access device tree properties.

Device controller
-----------------

.. function:: dts_basic.device_tree_controller_count(device_type_name [, default="<unset>"])

    Get the number of activated devices of given type.

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :return: number of activated devices

.. function:: dts_basic.device_tree_controller_prefix(device_type_name, device_index [, default="<unset>"])

    Get the device tree prefix for the device of the given type and index.

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :param device_index: Index of device
    :return: device tree prefix (e.g. ST_STM32_SPI_FIFO_4000000)

.. function:: dts_basic.device_tree_controller_property(device_type_name, device_index, property_name [, default="<unset>"])

    Get device tree property value for the device of the given type and index.

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :param device_index: Index of device
    :param property_name: Property name of the device tree property
                          (e.g. 'BASE_ADDRESS', 'LABEL', 'IRQ_0', ...)
    :return: property value as given in generated_dts_board.conf

.. function:: dts_basic.device_tree_controller_property_indirect(device_type_name, device_index, property_name, property_name_indirect [, default="<unset>"])

    Get the property of another device given by a property.

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :param device_index: Index of device
    :param property_name: Property that denotes the device tree prefix of the other device
    :param property_name_indirect: Property name of the other device property
                                   (e.g. 'BASE_ADDRESS', 'LABEL', 'IRQ_0', ...)
    :return: property value as given in generated_dts_board.conf

.. function:: dts_basic.device_tree_controller_compatible_x(device_type_name, device_index, compatible [, default="<unset>"])

    Check compatibility to device given by type and index.

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :param device_index: Index of device
    :param compatible: driver compatibility string (e.g. st,stm32-spi-fifo)
    :return: 1 if compatible, 0 otherwise

.. function:: dts_basic.device_tree_controller_compatible(device_type_name, compatible)

    Check compatibility to at least one activated device of given type.

    The compatible parameter is checked against the compatible property of
    all activated devices of given type.

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :param compatible: driver compatibility string (e.g. st,stm32-spi-fifo)
    :return: 1 if there is compatibility to at least one activated device,
             0 otherwise

.. function:: dts_basic.device_tree_controller_data_name(device_type_name, device_index, data)

    Get the name of the driver data.

    Generates an unique name for driver data.

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :param device_index: Index of device
    :param data: suffix for data (e.g. 'config')
    :return: controller data name (e.g. ST_STM32_SPI_FIFO_4000000_config)

.. function:: dts_basic.device_tree_controller_device_name(device_type_name, device_index)

    Get the device name.

    The device tree prefix of the device is used as the device name.

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :param device_index: Index of device
    :return: device name (e.g. ST_STM32_SPI_FIFO_4000000)

.. function:: dts_basic.device_tree_controller_driver_name(device_type_name, device_index)

    Get the driver name.

    This is a convenience function for:

    - codegen.device_tree_controller_property(device_type_name, device_index, 'LABEL')

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :param device_index: Index of device
    :return: driver name (e.g. "SPI_0")

.. function:: dts_basic.device_tree_controller_driver_name_indirect(device_type_name, device_index, property_name)

     Get the driver name of another device given by the property.

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :param device_index: Index of device
    :param property_name: Property that denotes the device tree prefix of the other device
    :return: driver name of other device (e.g. "GPIOA")

Guarding chunks of source code
------------------------------

.. function:: dts_basic.if_device_tree_controller_compatible(device_type_name, compatible)

    Stop code generation if there is no activated device that is compatible.

    Code generation stops right before the generator end marker @code{.codeins}@endcode.

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :param compatible: driver compatibility string (e.g. st,stm32-spi-fifo)

.. function:: dts_basic.outl_guard_device_tree_controller(device_type_name, compatible)

    Write a guard (#if [guard]) C preprocessor directive to output.

    If there is an activated device that is compatible the guard value is set to 1,
    otherwise it is set to 0.

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :param compatible: driver compatibility string (e.g. st,stm32-spi-fifo)

.. function:: dts_basic.outl_unguard_device_tree_controller(device_type_name, compatible)

    Write an unguard (#endif) C preprocessor directive to output.

    This is the closing command for codegen.outl_guard_device_tree_controller().

    :param device_type_name: Type of device controller (e.g. 'SPI', 'GPIO', 'PIN', ...)
    :param compatible: driver compatibility string (e.g. st,stm32-spi-fifo)
