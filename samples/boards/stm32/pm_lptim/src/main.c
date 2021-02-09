/*
 * Copyright (c) 2016 Intel Corporation.
 * Copyright (c) 2020 STMicroelectronics.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr.h>

#include <string.h>
#include <soc.h>
#include <device.h>
#include <drivers/gpio.h>
#include <sys/printk.h>

const struct device *gpio_bn, *gpio_led, *gpio_mco;

bool ready_to_sleep;

/* in msec */
/* setting to K_TICKS_FOREVER willl activate the deepsleep mode */
#define SLEEP_TIME 4000

#define DEMO_DESCRIPTION	\
	"Demo Description\n"	\
	"Application is demonstrating the low power " \
	"with the LPTIM used as systick.\n" \
	"The system goes to sleep mode on k_sleep() when pressing the button\n" \
	"(led off) and wakes up by the lptim timeout expiration (led on)\n\n" \

/* The devicetree node identifier for the "sw0" alias. */
#define SW0_NODE DT_ALIAS(sw0)
/* GPIO for the User push button */
#if DT_NODE_HAS_STATUS(SW0_NODE, okay)
#define SW	DT_GPIO_LABEL(SW0_NODE, gpios)
#define PIN	DT_GPIO_PIN(SW0_NODE, gpios)
#if DT_PHA_HAS_CELL(SW0_NODE, gpios, flags)
#define SW0_FLAGS DT_GPIO_FLAGS(SW0_NODE, gpios)
#else
#define SW0_FLAGS 0
#endif
#else
/* A build error here means your board isn't set up to input a button. */
#error "Unsupported board: sw0 devicetree alias is not defined"
#endif

/* The devicetree node identifier for the "led0" alias. */
#define LED0_NODE DT_ALIAS(led0)
/* GPIO for the Led */
#define LED0	DT_GPIO_LABEL(LED0_NODE, gpios)
#define PIN0	DT_GPIO_PIN(LED0_NODE, gpios)
#define LED0_FLAGS DT_GPIO_FLAGS(LED0_NODE, gpios)

#define MCO_NODE DT_ALIAS(mco)
#define MCO	DT_GPIO_LABEL(MCO_NODE, gpios)
#define MCO_PIN	DT_GPIO_PIN(MCO_NODE, gpios)
#define MCO_FLAGS DT_GPIO_FLAGS(MCO_FLAGS, gpios)

static struct gpio_callback gpio_cb;

void button_pressed(const struct device *dev, struct gpio_callback *cb,
		    uint32_t pins)
{
	ARG_UNUSED(dev);
	ARG_UNUSED(pins);
	ARG_UNUSED(cb);

	/* Turn LED off */
	gpio_pin_set(gpio_led, PIN0, 0);
	ready_to_sleep = true;
}

/* Application main Thread */
void main(void)
{
	bool back = false;

	printk("\n\n*** Low power Management Demo on %s ***\n", CONFIG_BOARD);
	printk(DEMO_DESCRIPTION);

	ready_to_sleep = false;
	gpio_bn = device_get_binding(SW);
	gpio_mco = device_get_binding(MCO);

	/* Configure Button 1 to wakeup from sleep mode */
	gpio_pin_configure(gpio_bn, PIN, SW0_FLAGS | GPIO_INPUT);
	gpio_pin_interrupt_configure(gpio_bn, PIN, GPIO_INT_EDGE_TO_ACTIVE);
	gpio_init_callback(&gpio_cb, button_pressed, BIT(PIN));
	gpio_add_callback(gpio_bn, &gpio_cb);

	/* Configure LEDs */
	gpio_led = device_get_binding(LED0);
	if (gpio_led == NULL) {
		return;
	}

	if (gpio_pin_configure(gpio_led, PIN0,
			GPIO_OUTPUT_ACTIVE | LED0_FLAGS) < 0) {
		return;
	}

	if (gpio_pin_configure(gpio_mco, MCO_PIN,
			GPIO_OUTPUT_ACTIVE | MCO_FLAGS) < 0) {
		return;
	}

	/* Set MCO PIN to default value */
	gpio_pin_set(gpio_mco, MCO_PIN, 0);

	gpio_pin_set(gpio_led, PIN0, 1);


	/*
	 * Start the demo.
	 */

	while (1) {
		if (ready_to_sleep == true) {
			gpio_pin_set(gpio_led, PIN0, 0);
			ready_to_sleep = false;
			back = true;
			/* MCO pin set */
			gpio_pin_set(gpio_mco, MCO_PIN, 1);
			k_msleep(SLEEP_TIME);
		}

		if (back) {
			gpio_pin_set(gpio_led, PIN0, 1);
			printk("We're back !!\n");
			/* MCO Pin reset */
			gpio_pin_set(gpio_mco, MCO_PIN, 0);
			back = false;
		};
	}
}
