# Copyright (c) 2018 Linaro Limited
#
# SPDX-License-Identifier: Apache-2.0

import pprint
import codegen
import re
from string import Template

# Provide a device tree specific substition pattern
# Only "braced" pattern should be used. TODO: prevent substitution w/o braces
# Allowed chars are speficied by device tree specification: ,._+?@/#a-zA-Z0-9,
# plus '@' used to detect a dts path is provided
DEVICE_TREE_SUB_PATTERN='''
\$(?:
  (?P<escaped>\$) |   # Escape sequence of two delimiters
  (?P<named>[_a-z][_a-z0-9]*)      |   # delimiter and a Python identifier
  {(?P<braced>[@,._+?/#a-zA-Z0-9-]*)}   |   # delimiter and a braced identifier
  (?P<invalid>)              # Other ill-formed delimiter exprs
)
'''

def device_declare(compatibles, init_prio_flag, kernel_level, irq_func,
                    init_func, api, data_struct, config_struct):

    codegen.edevice_tree_set_drivers_compatibles(compatibles)

    _prio = init_prio_flag
    _level = kernel_level
    _isr = irq_func
    _device_init = init_func
    _api = api
    _data_struct = data_struct
    _config_struct = config_struct

    for node_label in codegen.edevice_tree_compatible_labels():
        dev_idx = codegen.label_to_index(node_label)
        _dev_name = codegen.device_tree_device_instance_name(dev_idx)
        _config_irq = codegen.device_tree_node_struct_name(dev_idx, 'config_irq')
        _drv_name = codegen.edevice_tree_node_property(dev_idx, 'label')
        _data = codegen.device_tree_node_struct_name(dev_idx, 'data')
        _config_info = codegen.device_tree_node_struct_name(dev_idx, 'config')

        codegen.outl('\n#ifdef CONFIG_{}\n'.format(_drv_name.strip('"')))

        # config irq
        if codegen.config_property(_isr['irq_flag'], 0):
           codegen.outl('DEVICE_DECLARE({});'.format(_dev_name))
           codegen.outl('static void {}(struct device *dev)'.format(_config_irq))
           codegen.outl('{')
           device_generate_irq_bootstrap(dev_idx, _isr, _dev_name)
           codegen.outl('}')
           codegen.outl('')
        #
        # config info
        device_generate_struct('config', dev_idx, _config_struct)

        # config data
        device_generate_struct('data', dev_idx, _data_struct)

        #
        #device init
        codegen.outl('DEVICE_AND_API_INIT({},'.format(_dev_name))
        codegen.outl('\t{},'.format(_drv_name))
        codegen.outl('\t{},'.format(_device_init))
        codegen.outl('\t&{},'.format(_data))
        codegen.outl('\t&{},'.format(_config_info))
        codegen.outl('\t{},'.format(_level))
        codegen.outl('\t{},'.format(_prio))
        codegen.outl('\t&{});'.format(_api))
        codegen.outl('')
        codegen.outl('#endif /* CONFIG_{} */\n'.format(_drv_name.strip('"')))

    codegen.edevice_tree_unset_drivers_compatibles()


def device_generate_struct(type_of_struct, _dev_idx, _struct):

    dev_idx = _dev_idx
    mapping = {}

    # convert _struct into a list. Struct might have only on
    if type(_struct) is str:
        _struct = [_struct]
    else:
        _struct = list(_struct)

    if type_of_struct == 'config':
        codegen.out('static const struct {} {} = {{'.format(_struct[0],
                        codegen.device_tree_node_struct_name(dev_idx, 'config')))
    elif type_of_struct == 'data':
        codegen.out('static struct {} {} = {{'.format(_struct[0],
                        codegen.device_tree_node_struct_name(dev_idx, 'data')))
    else:
        msg("Not expected")

    if len(_struct) > 1:
        # Find elements to subsitute in given string
        elements_to_substitute = re.findall('\$\{(.*?)\}', _struct[1])

        # Fill mapping dict with subsitutes to elemments
        for element in elements_to_substitute:
            if element == 'node_index':
                mapping[element] = dev_idx
            else:
                dt_path = element.strip('@')
                mapping[element] = codegen.edevice_tree_node_property(dev_idx, dt_path)

        pprint.pprint("mapping: {}".format(mapping))
        # Update default Template 'braced' finder to support
        # valid characters for device tree property names
        Template.pattern = re.compile(DEVICE_TREE_SUB_PATTERN, re.IGNORECASE|re.VERBOSE)

        # Perform the substitution and display the string
        codegen.out('{}'.format(Template(_struct[1]).safe_substitute(mapping)))

    codegen.outl('};')
    codegen.outl('')

def device_generate_irq_bootstrap(dev_idx, isr, dev_name):

    irq_list = codegen.edevice_tree_node_property(dev_idx, 'interrupts')
    irq_names = codegen.edevice_tree_node_property(dev_idx, 'interrupt-names')

    try:
        irq_labels = irq_list[0]['labels']
    except KeyErrror:
        msg("No IRQ labels")

    for i in range (0, len(irq_list)):
        i_num = codegen.edevice_tree_node_property(dev_idx, 'interrupts/' + str(i) + '/irq')
        i_prio = codegen.edevice_tree_node_property(dev_idx, 'interrupts/' + str(i) + '/priority')
        codegen.outl('\tIRQ_CONNECT({},'.format(i_num))
        codegen.outl('\t\t{},'.format(i_prio))
        if irq_names is not None:
            codegen.outl('\t\t{}_{},'.format(isr['irq_func'], irq_names[i]))
        else:
            codegen.outl('\t\t{},'.format(isr['irq_func']))
        codegen.outl('\t\tDEVICE_GET({}),'.format(dev_name))
        codegen.outl('\t\t0);')
        codegen.outl('\tirq_enable({});'.format(i_num))
