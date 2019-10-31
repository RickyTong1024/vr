#!/usr/bin/env python  
#coding=utf-8

class ng_instance():
    @classmethod
    def instance(cls):
        if hasattr(cls, 'inst'):
            return cls.inst
        else:
            obj = cls()
            cls.inst = obj
            return obj
