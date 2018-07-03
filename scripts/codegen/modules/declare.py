# Copyright (c) 2018 Linaro Limited
#
# SPDX-License-Identifier: Apache-2.0

import pprint
import codegen

def device_declare(compatible, init_prio_flag, kernel_level, irq_func,
                    init_func, api, data_struct, config_struct):

    codegen.edevice_tree_set_drivers_compatibles(compatible)

    _prio = codegen.config_property(init_prio_flag, 0)
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
        _irq = codegen.edevice_tree_node_property(dev_idx, 'interrupts/irq')
        _irq_prio = codegen.edevice_tree_node_property(dev_idx, 'interrupts/priority')
        _drv_name = codegen.edevice_tree_node_property(dev_idx, 'label')
        _data = codegen.device_tree_node_struct_name(dev_idx, 'data')
        _config_info = codegen.device_tree_node_struct_name(dev_idx, 'config')

        codegen.outl('\n#ifdef CONFIG_{}\n'.format(_drv_name.strip('"')))

        # config irq
        if codegen.config_property(_isr['irq_flag'], 0):
           codegen.outl('DEVICE_DECLARE({});'.format(_dev_name))
           codegen.outl('static void {}(struct device *dev)'.format(_config_irq))
           codegen.outl('{')
           codegen.outl('\tIRQ_CONNECT({},'.format(_irq))
           codegen.outl('\t\t{},'.format(_irq_prio))
           codegen.outl('\t\t{},'.format(_isr['irq_func']))
           codegen.outl('\t\tDEVICE_GET({}),'.format(_dev_name))
           codegen.outl('\t\t0);')
           codegen.outl('\tirq_enable({});'.format(_irq))
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


def device_generate_struct(type_of_struct, _dev_idx, _struct):

    dev_idx = _dev_idx
    struct = _struct

    if type_of_struct == 'config':
        codegen.outl('static const struct {} {} = {{'.format(_struct[0],
                        codegen.device_tree_node_struct_name(dev_idx, 'config')))
    elif type_of_struct == 'data':
        codegen.outl('static struct {} {} = {{'.format(_struct[0],
                        codegen.device_tree_node_struct_name(dev_idx, 'data')))
    else:
        msg("Not expected")

    for line_idx in range(1, len(_struct) ):
        # print the #ifdef <flag> if any
        if 'flag' in _struct[line_idx]:
            codegen.outl('#ifdef {}'.format(_struct[line_idx]['flag']))

        # treat strings line
        if 'string' in _struct[line_idx]:
            codegen.out('\t')
            for str_idx in range(len(_struct[line_idx]['string'])):
                if _struct[line_idx]['string'][str_idx] is 'index':
                    # tag 'index' should be replaced with device index
                    string = str(dev_idx)
                else:
                    string = _struct[line_idx]['string'][str_idx]
                codegen.out('{}'.format(string))
            codegen.out(',\n')
            # print the #endif /* <flag> */
            if 'flag' in _struct[line_idx]:
                codegen.outl('#endif /* {} */'.format(
                                            _struct[line_idx]['flag']))
            #for now string and values lines could not mix, continue
            continue

        # Deal with struct = value lines
        if _struct[line_idx]['value'].find('@') == 0:
            # starts with '@', look in device tree
            value = _struct[line_idx]['value'].strip('@')
            value = codegen.edevice_tree_node_property(dev_idx, value)
        else:
            # use as is
            value = _struct[line_idx]['value']
        if 'cast' in _struct[line_idx]:
            # line is of type: field = (type)value,
            codegen.outl('\t{} = {}{},'.format(
                _struct[line_idx]['field'], _struct[line_idx]['cast'],
                                                                value))
        else:
            # line is of type: field = value,
            codegen.outl('\t{} = {},'.format(_struct[line_idx]['field'],
                                                                value))
        # print the #endif /* <flag> */
        if 'flag' in _struct[line_idx]:
            codegen.outl('#endif /* {} */'.format(
                                        _struct[line_idx]['flag']))
    codegen.outl('};')
    codegen.outl('')
