# noinspection PyProtectedMember
from typing import Annotated, _AnnotatedAlias
from collections import ChainMap
from enum import Enum


class LabelStyle(Enum): Left, Top, Off = 0, 1, 2


class _MetaWidget(type):
    @staticmethod
    def is_dunder(name):
        return name.startswith("__") and name.endswith("__")

    @staticmethod
    def generate_new_method(class_instance, T, label_style, fields):
        def instantiate_class(cls, label, group = "", *args, **kwargs):
            # Create instance
            instance = super(class_instance, cls).__new__(cls)
            if type(instance) is _AnnotatedAlias:
                instance = instance.__metadata__[0]

            # Update default members
            for arg, key in zip(args, fields):
                fields[key] = arg

            # Update kwargs
            for key, arg in kwargs.items():
                if key in fields:
                    fields[key] = arg
                else:
                    raise Exception(f"[ERROR] {key} non existent argument")

            # Store args in obj instance
            for key, value in fields.items():
                setattr(instance, key, value)

            # add 'label' and 'group' dunder members to the instance
            instance.__label_style__ = label_style
            instance.__label__ = label
            instance.__group__ = group
            instance.__type__ = T

            # build an annotation with the args
            return Annotated[T, instance]

        def unlabeled_new(cls, group = "", *args, **kwargs):
            return instantiate_class(cls, None, group=group, *args, **kwargs)

        def labeled_new(cls, label = "Name", group = "", *args, **kwargs):
            return instantiate_class(cls, label, group=group, *args, **kwargs)

        return unlabeled_new if label_style == LabelStyle.Off else labeled_new

    def __new__(mcs, name, bases, members, T = None, label_style = LabelStyle.Left):
        # Define the new class
        class_instance = super().__new__(mcs, name, bases, members)

        complete_hierarchy = set()
        for base in bases:
            complete_hierarchy = complete_hierarchy.union(set(base.__mro__))

        fields = dict()
        for base in complete_hierarchy:
            for field_name, value in base.__dict__.items():
                if not _MetaWidget.is_dunder(field_name):
                    fields[field_name] = value

        for field_name, value in members.items():
            if not _MetaWidget.is_dunder(field_name):
                fields[field_name] = value

        class_instance.__new__ = _MetaWidget.generate_new_method(class_instance, T, label_style, fields)

        return class_instance


class Widget(metaclass=_MetaWidget):
    """ Base widget class """

    __label__ = ""
    """ Widget's label text """

    __group__ = ""
    """ Widget's group name """

    __type__ = None
    """ Widget's tracked data type """

    __label_style__ = LabelStyle.Left
    """ The widgets label style, currently can be set to None, Top or Left """

    def __widget__(self, bind, default):
        """ Cmds Method that build the widget in maya """
        print("Abstract method invoked directly")


class Fragment:
    """ This class is an organized metadata info blob referred to a single variable field contained in a major object,
        Many metadata fragments account for an object's full fields meta reflection """

    def __init__(self, target_ref: object, field_name: str, default_value: object, data: Widget) -> None:
        self.bind: tuple[object, str] = target_ref, field_name
        """ The bind, represents the path to reach this variable's reference in memory, its represented by the object containing the variable and the variable's name """

        self.default: object = default_value
        """ This value refer to the variable's default value """

        self.data: Widget = data

    def build_widget(self):
        self.data.__widget__(self.bind, self.default)

    @staticmethod
    def extract_reflection(target: object) -> dict[str, list]:
        """ Extract the reflection from the target's instance and populate a dictionary of fragments """
        fragment_groups = {}
        ungrouped_fragments = []
        defaults_values = ChainMap(*(c.__dict__ for c in type(target).__mro__))

        for field_name, field_metadata in ChainMap(*(c.__annotations__ for c in type(target).__mro__ if '__annotations__' in c.__dict__)).items():  # For each metadata blob acquired from the target
            if not isinstance(field_metadata, _AnnotatedAlias):
                continue
            instance = field_metadata.__metadata__[0]
            if not issubclass(type(instance), Widget):
                continue

            fragment = Fragment(target, field_name, defaults_values[field_name], instance)  # Build the reflection fragment using the metadata blob
            (fragment_groups.setdefault(fragment.data.__group__, []) if fragment.data.__group__ else ungrouped_fragments).append(fragment)  # adds it to the groups or ungroup if it has a group

        if ungrouped_fragments:  # Append the ungrouped fragments at the end of the fragment group's dictionary
            fragment_groups[""] = ungrouped_fragments
        return fragment_groups
