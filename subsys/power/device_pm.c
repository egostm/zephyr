/*
 * Copyright (c) 2018 Intel Corporation.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr.h>
#include <kernel.h>
#include <device.h>
#include <sys/__assert.h>

#define LOG_LEVEL CONFIG_PM_LOG_LEVEL /* From power module Kconfig */
#include <logging/log.h>
LOG_MODULE_DECLARE(power);

/* Device PM request type */
#define DEVICE_PM_SYNC   BIT(0)
#define DEVICE_PM_ASYNC  BIT(1)

/* Device PM states */
enum device_pm_state {
	DEVICE_PM_STATE_ACTIVE = 1,
	DEVICE_PM_STATE_SUSPENDED,
	DEVICE_PM_STATE_SUSPENDING,
	DEVICE_PM_STATE_RESUMING,
};

static void device_pm_callback(const struct device *dev,
			       int retval, uint32_t *state, void *arg)
{
	__ASSERT(retval == 0, "Device set power state failed");

	/* Set the fsm_state */
	if (*state == DEVICE_PM_ACTIVE_STATE) {
		atomic_set(&dev->pm->fsm_state,
			   DEVICE_PM_STATE_ACTIVE);
	} else {
		atomic_set(&dev->pm->fsm_state,
			   DEVICE_PM_STATE_SUSPENDED);
	}

	/*
	 * This function returns the number of woken threads on success. There
	 * is nothing we can do with this information. Just ignore it.
	 */
	(void)k_condvar_broadcast(&dev->pm->condvar);
}

static void pm_work_handler(struct k_work *work)
{
	struct device_pm *pm = CONTAINER_OF(work,
					struct device_pm, work);
	const struct device *dev = pm->dev;
	int ret = 0;

	switch (atomic_get(&dev->pm->fsm_state)) {
	case DEVICE_PM_STATE_ACTIVE:
		if ((atomic_get(&dev->pm->usage) == 0) &&
					dev->pm->enable) {
			atomic_set(&dev->pm->fsm_state,
				   DEVICE_PM_STATE_SUSPENDING);
			ret = device_set_power_state(dev,
						DEVICE_PM_SUSPEND_STATE,
						device_pm_callback, NULL);
		} else {
			goto fsm_out;
		}
		break;
	case DEVICE_PM_STATE_SUSPENDED:
		if ((atomic_get(&dev->pm->usage) > 0) ||
					!dev->pm->enable) {
			atomic_set(&dev->pm->fsm_state,
				   DEVICE_PM_STATE_RESUMING);
			ret = device_set_power_state(dev,
						DEVICE_PM_ACTIVE_STATE,
						device_pm_callback, NULL);
		} else {
			goto fsm_out;
		}
		break;
	case DEVICE_PM_STATE_SUSPENDING:
	case DEVICE_PM_STATE_RESUMING:
		/* Do nothing: We are waiting for device_pm_callback() */
		break;
	default:
		LOG_ERR("Invalid FSM state!!\n");
	}

	__ASSERT(ret == 0, "Set Power state error");
	return;

fsm_out:
	/*
	 * This function returns the number of woken threads on success. There
	 * is nothing we can do with this information. Just ignoring it.
	 */
	(void)k_condvar_broadcast(&dev->pm->condvar);
}

static int device_pm_request(const struct device *dev,
			     uint32_t target_state, uint32_t pm_flags)
{
	struct k_mutex request_mutex;

	__ASSERT((target_state == DEVICE_PM_ACTIVE_STATE) ||
			(target_state == DEVICE_PM_SUSPEND_STATE),
			"Invalid device PM state requested");

	if (target_state == DEVICE_PM_ACTIVE_STATE) {
		if (atomic_inc(&dev->pm->usage) < 0) {
			return 0;
		}
	} else {
		if (atomic_dec(&dev->pm->usage) > 1) {
			return 0;
		}
	}

	if (k_is_pre_kernel()) {
		/* If we are being called before the kernel was initialized
		 * we can assume that the system took care of initialized
		 * devices properly. It means that all dependencies were
		 * satisfied and this call just incremented the reference count
		 * for this device.
		 */
		return 0;
	}

	(void)k_work_schedule(&dev->pm->work, K_NO_WAIT);

	/* Return in case of Async request */
	if (pm_flags & DEVICE_PM_ASYNC) {
		return 0;
	}

	k_mutex_init(&request_mutex);
	k_mutex_lock(&request_mutex, K_FOREVER);
	(void)k_condvar_wait(&dev->pm->condvar, &request_mutex, K_FOREVER);
	k_mutex_unlock(&request_mutex);

	/*
	 * dev->pm->fsm_state was set in device_pm_callback(). As the device
	 * may not have been properly changed to the target_state or another
	 * thread we check it here before returning.
	 */
	return target_state == atomic_get(&dev->pm->fsm_state) ? 0 : -EIO;
}

int device_pm_get(const struct device *dev)
{
	return device_pm_request(dev,
			DEVICE_PM_ACTIVE_STATE, DEVICE_PM_ASYNC);
}

int device_pm_get_sync(const struct device *dev)
{
	return device_pm_request(dev, DEVICE_PM_ACTIVE_STATE, 0);
}

int device_pm_put(const struct device *dev)
{
	return device_pm_request(dev,
			DEVICE_PM_SUSPEND_STATE, DEVICE_PM_ASYNC);
}

int device_pm_put_sync(const struct device *dev)
{
	return device_pm_request(dev, DEVICE_PM_SUSPEND_STATE, 0);
}

void device_pm_enable(const struct device *dev)
{
	if (k_is_pre_kernel()) {
		dev->pm->dev = dev;
		dev->pm->enable = true;
		atomic_set(&dev->pm->fsm_state, DEVICE_PM_STATE_SUSPENDED);
		k_work_init_delayable(&dev->pm->work, pm_work_handler);
		return;
	}

	k_sem_take(&dev->pm->lock, K_FOREVER);
	dev->pm->enable = true;

	/* During the driver init, device can set the
	 * PM state accordingly. For later cases we need
	 * to check the usage and set the device PM state.
	 */
	if (!dev->pm->dev) {
		dev->pm->dev = dev;
		atomic_set(&dev->pm->fsm_state,
			   DEVICE_PM_STATE_SUSPENDED);
		k_work_init_delayable(&dev->pm->work, pm_work_handler);
	} else {
		k_work_schedule(&dev->pm->work, K_NO_WAIT);
	}
	k_sem_give(&dev->pm->lock);
}

void device_pm_disable(const struct device *dev)
{
	__ASSERT(k_is_pre_kernel() == false, "Device should not be disabled "
		 "before kernel is initialized");

	k_sem_take(&dev->pm->lock, K_FOREVER);
	dev->pm->enable = false;
	/* Bring up the device before disabling the Idle PM */
	k_work_schedule(&dev->pm->work, K_NO_WAIT);
	k_sem_give(&dev->pm->lock);
}
