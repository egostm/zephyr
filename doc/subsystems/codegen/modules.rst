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


This section is deprecated in current pull request



Device declare module
*********************

::

    codegen.import_module('declare_template')


The module provides a simple API for driver devices instantiation

Declaring a driver
------------------

.. function:: declare_template.device_declare(compatibles, init_prio_flag, kernel_level, irq_func, init_func, api, data_struct, config_struct)

Generate device instances code for all devices activated ('status' = 'ok') in board device tree file
matching the provided compatibles.
Most of the parameters provided aim at filling DEVICE_AND_API_INIT macro. Other parameters are there
to help code generation to fit driver specifics.
Generated instance code will be set under Kconfig variable which name is build with device node label name
(e.g: CONFIG_I2C_1).

    :compatibles: List of compatibles supported by the driver (e.g. ['st,stm32-spi-fifo', 'st,stm32-spi'])
    :init_prio_flag: Flag for driver activation priority (e.g. CONFIG_KERNEL_INIT_PRIORITY_DEVICE)
    :kernel_level: Flag for driver activation priority (e.g. POST_KERNEL)
    :irq_func: Two elements python dict providing driver isr function prefix (e.g. 'irq_func':'stm32_i2c_isr')
                     and flag to be used for driver IRQ code control (e.g. 'irq_flag': 'CONFIG_I2C_STM32_INTERRUPT').
                     If irq_func is 'None', no IRQ code is generated.
                     'device_declare' will  generate as much IRQ code as declared by device node.
                     If 'interrupts-names' property if provided in node, isr names will be generated using matching
                     values as function postfixs.
    :init_func: Name of the driver init function (e.g. 'i2c_stm32_init').
    :api: Name of the driver api structure  (e.g. 'api_funcs').
    :data_struct: Two elements python list providing elements for driver '_data' structure generation.
    :config_struct: Two elements python list providing elements for driver '_config' structure generation.

'data_struct' and 'config_struct' will be processed the same way:

* First element (e.g. 'i2c_stm32_config') should be the structure name.
* Second element is a 'c' template code between triple double quotes (""" """). It should provide the expected code to be generated for the structure. For instance:

.. code-block:: python

    """
    	.i2c = (I2C_TypeDef *)${@reg/0},
    	.pclken = {
    			.enr = ${@clock/bits},
    			.bus = ${@clock/bus},
    	},
    #ifdef CONFIG_I2C_STM32_INTERRUPT
    	.irq_config_func = st_stm32_i2c_v1_${node_index}_config_irq,
    #endif
    	.bitrate = ${@clock-frequency},
    """

This templates features two types of placeholders that we be substituted by expected matching values:

* ${node_index}: will be replaced by device instance node property 'label' if provided or numeric index otherwise.
* ${@'path to dts property'}: will be replaced by provided device node property. This path supports every node property that is documented in node yaml bindings. It also supports yaml heuristics, like 'bus-master' and will use documented '"#cells"'.

If the second element of 'data_struct' or 'config_struct' list is not provided, an empty structure is generated.

Finally, for the above depicted example, 'device_declare' will generate, for device instance 'I2C1':

.. code-block:: c

    #ifdef CONFIG_I2C_1

    #ifdef CONFIG_I2C_STM32_INTERRUPT
    DEVICE_DECLARE(st_stm32_i2c_v1_i2c_1);
    static void st_stm32_i2c_v1_i2c_1_config_irq(struct device *dev)
    {
    	IRQ_CONNECT(31,
    		0,
    		stm32_i2c_isr_event,
    		DEVICE_GET(st_stm32_i2c_v1_i2c_1),
    		0);
    	irq_enable(31);
    	IRQ_CONNECT(32,
    		0,
    		stm32_i2c_isr_error,
    		DEVICE_GET(st_stm32_i2c_v1_i2c_1),
    		0);
    	irq_enable(32);
    }
    #endif /* CONFIG_I2C_STM32_INTERRUPT */

    static const struct i2c_stm32_config st_stm32_i2c_v1_i2c_1_config = {
    	.i2c = (I2C_TypeDef *)0x40005400,
    	.pclken = {
    		.enr = 131072,
    		.bus = 2,
    	},
    #ifdef CONFIG_I2C_STM32_INTERRUPT
    	.irq_config_func = st_stm32_i2c_v1_i2c_1_config_irq,
    #endif
    	.bitrate = 400000,
    };

    static struct i2c_stm32_data st_stm32_i2c_v1_i2c_1_data = {};

    DEVICE_AND_API_INIT(st_stm32_i2c_v1_i2c_1,
    	"I2C_1",
    	i2c_stm32_init,
    	&st_stm32_i2c_v1_i2c_1_data,
    	&st_stm32_i2c_v1_i2c_1_config,
    	POST_KERNEL,
    	CONFIG_KERNEL_INIT_PRIORITY_DEVICE,
    	&api_funcs);
    #endif /* CONFIG_I2C_1 */
