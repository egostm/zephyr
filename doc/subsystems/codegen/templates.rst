..
    Copyright (c) 2018 Bobby Noelte
    SPDX-License-Identifier: Apache-2.0

.. _codegen_templates:

Code Generation Templates
#########################

Code generation templates provide sopisticated code generation functions.

.. contents::
   :depth: 2
   :local:
   :backlinks: top

Templates have to be included to gain access to the template's functions
and variables.

 ::

    /* This file uses templates. */
    ...
    /**
     * @code{.codegen}
     * template_in_var = 1
     * codegen.out_include('templates/template_tmpl.c')
     * if template_out_var not None:
     *     codegen.outl("int x = %s;" % template_out_var)
     * @endcode{.codegen}
     */
    /** @code{.codeins}@endcode */
    ...

Device drivers
**************

Simple drivers
--------------

::

    codegen.out_include('templates/drivers/simple_tmpl.c')

The template generates code for simple driver instantiation.

The template expects the following globals to be set:

.. attribute:: device_type

    Type of device (e.g. 'UART', 'GPIO', ...)

.. attribute:: device_configs

    A list of configuration variables for device instantiation.
    (e.g. ['CONFIG_SPI_0', 'CONFIG_SPI_1'])

.. attribute:: driver_names

    A list of driver names for device instantiation. The list shall be ordered
    as the list of device configs. Watch for the '"' of the driver names.
    (e.g. ['"SPI_0"', '"SPI_1"'])

.. attribute:: device_inits

    A list of device initialisation functions or a one single function. The
    list shall be ordered as the list of device configs.
    (e.g. 'spi_stm32_init')

.. attribute:: device_levels

    A list of driver initialisation levels or one single level definition. The
    list shall be ordered as the list of device configs.
    (e.g. 'PRE_KERNEL_1')

.. attribute:: device_prios

    A list of driver initialisation priorities or one single priority
    definition. The list shall be ordered as the list of device configs.
    (e.g. 32)

.. attribute:: device_api

    Identifier of the device api.
    (e.g. 'spi_stm32_driver_api')

.. attribute:: device_data

    device data type definition (e.g. 'struct spi_stm32_data') and
    an optional code template for data initialisation.

.. attribute:: device_config_info

    Device config type definition (e.g. 'struct spi_stm32_data') and
    a code template for configuration initialisation.

.. attribute:: device_config_irq

    A code template for interrupt configuration initialisation.

Usage example:

::

    /**
     * @code{.codegen}
     * device_type = 'SERIAL'
     * device_configs = ['CONFIG_UART_STM32_PORT_{}'.format(x) \
     *                   for x in range(1, 11)] + \
     *                  ['CONFIG_UART_STM32_LPUART_{}'.format(x) \
     *                   for x in range(1, 2)]
     * driver_names = ['"UART_{}"'.format(x) for x in range(1, 11)] + \
     *                ['"LPUART_{}"'.format(x) for x in range(1, 2)]
     * device_inits = 'uart_stm32_init'
     * device_levels = 'PRE_KERNEL_1'
     * device_prios = 'CONFIG_KERNEL_INIT_PRIORITY_DEVICE'
     * device_api = 'uart_stm32_driver_api'
     * device_data = ('struct uart_stm32_data', )
     * device_config_info = ('struct uart_stm32_config', \
     * """
     *         .uconf.base = (u8_t *)$BASE_ADDRESS,
     * #ifdef CONFIG_UART_INTERRUPT_DRIVEN
     *         .uconf.irq_config_func = ${DEVICE_CONFIG_IRQ},
     * #endif
     *         .pclken.bus = $CLOCK_0_BUS,
     *         .pclken.enr = $CLOCK_0_BITS,
     *         .baud_rate = ${CURRENT_SPEED},
     * """)
     * device_config_irq = \
     * """
     * #ifdef CONFIG_UART_INTERRUPT_DRIVEN
     * DEVICE_DECLARE(${DEVICE_NAME});
     * static void ${DEVICE_CONFIG_IRQ}(struct device *dev)
     * {
     *         IRQ_CONNECT(${IRQ_0}, ${IRQ_0_PRIORITY}, uart_stm32_isr, \\
     *                     DEVICE_GET(${DEVICE_NAME}), 0);
     *         irq_enable(${IRQ_0});
     * }
     * #endif
     * """
     * codegen.out_include('templates/drivers/simple_tmpl.c')
     * @endcode{.codegen}
     */
    /** @code{.codeins}@endcode */



Pin controller drivers
----------------------

::

    codegen.out_include('templates/drivers/pinctrl_tmpl.c')

The template generates the most part of a pinctrl driver including driver
instantiation.

 The template expects the following globals to be set:

.. attribute:: compatible

    The compatible string of the driver (e.g. 'st,stm32-pinctrl')

.. attribute:: data_info

    device data type definition (e.g. 'struct pinctrl_stm32_data')

.. attribute:: config_get

    C function name of device config_get function.

.. attribute:: mux_free

    C function name of device mux_free function.

.. attribute:: mux_get

    C function name of device mux_get function.

.. attribute:: mux_set

    C function name of device mux_set function.

.. attribute:: device_init

    C function name of device init function

.. attribute:: pinmux_pin(pinmux)

    Python function that extracts the pin number from the pinmux property.

.. attribute:: pinmux_mux(pinmux)

    Python function that extracts the mux value from the pinmux property.

Usage example:

::

    /**
     * @code{.codegen}
     * # compatible already set
     * config_get = 'pinctrl_stm32_config_get'
     * config_set = 'pinctrl_stm32_config_set'
     * mux_get = 'pinctrl_stm32_mux_get'
     * mux_set = 'pinctrl_stm32_mux_set'
     * device_init = 'pinctrl_stm32_device_init'
     * data_info = 'struct pinctrl_stm32_data'
     * def pinmux_pin(pinmux):
     *     return pinmux.split(',')[0]
     * def pinmux_mux(pinmux):
     *     return pinmux.split(',')[1]
     * codegen.out_include('templates/drivers/pinctrl_tmpl.c')
     * @endcode{.codegen}
     */
    /** @code{.codeins}@endcode */




