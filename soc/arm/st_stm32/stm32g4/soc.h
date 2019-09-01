/*
 * Copyright (c) 2019 Richard Osterloh <richard.osterloh@gmail.com>
 *
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * @file SoC configuration macros for the STM32G4 family processors.
 *
 * Based on reference manual:
 *   STM32G4xx advanced ARM ® -based 32-bit MCUs
 *
 * Chapter 2.2: Memory organization
 */


#ifndef _STM32G4_SOC_H_
#define _STM32G4_SOC_H_

#ifndef _ASMLANGUAGE

#include <autoconf.h>
#include <stm32g4xx.h>

/* ARM CMSIS definitions must be included before kernel_includes.h.
 * Therefore, it is essential to include kernel_includes.h after including
 * core SOC-specific headers.
 */
#include <kernel_includes.h>

#ifdef CONFIG_CLOCK_CONTROL_STM32_CUBE
#include <stm32g4xx_ll_utils.h>
#include <stm32g4xx_ll_bus.h>
#include <stm32g4xx_ll_rcc.h>
#include <stm32g4xx_ll_system.h>
#include <stm32g4xx_ll_pwr.h>
#endif /* CONFIG_CLOCK_CONTROL_STM32_CUBE */

#ifdef CONFIG_EXTI_STM32
#include <stm32g4xx_ll_exti.h>
#endif

#ifdef CONFIG_GPIO_STM32
#include <stm32g4xx_ll_gpio.h>
#endif

#ifdef CONFIG_SERIAL_HAS_DRIVER
#include <stm32g4xx_ll_usart.h>
#include <stm32g4xx_ll_lpuart.h>
#endif

#ifdef CONFIG_SPI_STM32
#include <stm32g4xx_ll_spi.h>
#endif

#ifdef CONFIG_I2C
#include <stm32g4xx_ll_i2c.h>
#endif

#ifdef CONFIG_IWDG_STM32
#include <stm32g4xx_ll_iwdg.h>
#endif

#ifdef CONFIG_ENTROPY_STM32_RNG
#include <stm32g4xx_ll_rng.h>
#endif

#if defined(CONFIG_RTC_STM32) || defined(CONFIG_COUNTER_RTC_STM32)
#include <stm32g4xx_ll_rtc.h>
#include <stm32g4xx_ll_exti.h>
#include <stm32g4xx_ll_pwr.h>
#endif

#ifdef CONFIG_ADC_STM32
#include <stm32g4xx_ll_adc.h>
#endif

#endif /* !_ASMLANGUAGE */

#endif /* _STM32G4_SOC_H_ */
