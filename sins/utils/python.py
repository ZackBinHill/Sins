def get_name_data_from_class_or_instance(class_or_instance):
    import inspect
    module_name = inspect.getmodule(class_or_instance).__name__
    class_name = (
        class_or_instance.__name__
        if inspect.isclass(class_or_instance)
        else class_or_instance.__class__.__name__
    )
    return module_name, class_name


def data_cmp(a, b):
    # print a, b
    if a is None:
        return -1
    elif b is None:
        return 1
    elif isinstance(a, dict) and isinstance(b, dict):
        # if a['value'] > b['value']:
        #     return 1
        # elif a['value'] < b['value']:
        #     return -1
        # else:
        #     return 0
        if 'value' in a:
            return data_cmp(a['value'], b['value'])
        elif 'object' in a:
            return data_cmp(a['object'].id, b['object'].id)
    else:
        if a > b:
            return 1
        elif a < b:
            return -1
        else:
            return 0


def get_class_from_name_data(module_name, class_name):
    module_ = __import__(module_name, fromlist=[class_name])
    return getattr(module_, class_name)


def sort_dict_by_keys(input_dict, reverse=False):
    return sorted(input_dict.items(), key=lambda t: t[0], reverse=reverse)


def sort_dict_by_values(input_dict, reverse=False):
    return sorted(input_dict.items(), key=lambda t: t[1], reverse=reverse)


def sort_dict_list_by_key(input_list, key, cmp=data_cmp, reverse=False):
    # print input_list, key
    return sorted(input_list, key=lambda x: x[key], cmp=cmp, reverse=reverse)


if __name__ == "__main__":
    from ui.widgets.previewlabel import PreviewLabel
    import datetime
    print get_name_data_from_class_or_instance(PreviewLabel)
    print get_class_from_name_data("ui.widgets.previewlabel", "ThumbnailLabel")
    print get_class_from_name_data("db.models", "Project")()

    l = [
        {'name': 'aa', 'age': None, 'dict': {'name': 'zz'}},
        {'name': 'bb', 'age': datetime.datetime.today(), 'dict': {'name': 'xx'}},
    ]
    print l
    print sort_dict_list_by_key(l, 'age', reverse=True)
    print l

    print sort_dict_by_keys({2:'bb', 1:"dd"})
    for i in sort_dict_by_keys({'1':'bb', '2':"dd"}, reverse=True):
        print i


