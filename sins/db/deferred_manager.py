# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/23/2018

from sins.module.db.peewee import DeferredForeignKey, ManyToManyField, DeferredThroughModel


class DeferredManager(object):
    def __init__(self):
        super(DeferredManager, self).__init__()
        self.fk_model_names = []
        self.deferred_fks = []
        self.links = {}

    def fk(self, fk_model_name, *args, **kwargs):
        if fk_model_name not in self.fk_model_names:
            self.fk_model_names.append(fk_model_name)
        deferred_fk = DeferredForeignKey(fk_model_name, *args, **kwargs)
        self.deferred_fks.append(deferred_fk)
        return deferred_fk

    def mtm(self, model_name, through_model_name, *args, **kwargs):
        deferred_through_model = DeferredThroughModel()
        many_to_many = ManyToManyField(model=model_name, through_model=deferred_through_model, *args, **kwargs)
        link = {}
        link['model_name'] = model_name
        link['field'] = many_to_many
        self.links[through_model_name] = link

        return many_to_many

    def connect(self, model_dict):
        for fk_model_name in self.fk_model_names:
            DeferredForeignKey.resolve(model_dict[fk_model_name])
        for through_model_name in self.links:
            link = self.links[through_model_name]
            many_to_many = link['field']
            many_to_many.rel_model = model_dict[link['model_name']]
            many_to_many.through_model.set_model(model_dict[through_model_name])

    def create_fk(self):
        for deferred_fk in self.deferred_fks:
            model = deferred_fk.model
            fk = getattr(model, deferred_fk.name)
            model._schema.create_foreign_key(fk)

