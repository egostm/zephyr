.. _Power-Management-LP-Timer:

Power Management LP Timer
#########################

Overview
********

This is a simple application which enter/exit the low power mode.
The led is ON in running mode and is switched off during low power periods.

.. _Power-Management-LP-Timer-requirements:

Requirements
************

You will see this error if you try to build sample for an unsupported board:

.. code-block:: none

   Unsupported board: led0 devicetree alias is not defined
   Unsupported board: sw0 devicetree alias is not defined

The board must have a user button and a LED connected via GPIO pins. These are called "User
LEDs" on many of Zephyr's :ref:`boards`. The Button and LED must be configured using the
``sw0`` :ref:`devicetree <dt-guide>` alias and
``led0`` :ref:`devicetree <dt-guide>` alias.
This is usually done in the :ref:`BOARD.dts file <devicetree-in-out-files>` or a :ref:`devicetree overlay
<set-devicetree-overlays>`.

Building and Running
********************

Build and flash sample as follows, changing ``nucleo_l4r5zi`` for your board:

.. zephyr-app-commands::
   :zephyr-app: samples/boards/stm32/pm_lptim
   :board: nucleo_l4r5zi
   :goals: build flash
   :compact:

After flashing, the LED is on, waiting for entering the low Power mode.
Press the User button to enter the low power mode. The led is off.
After three seconds the timeout wake the system and turn the led on again.
