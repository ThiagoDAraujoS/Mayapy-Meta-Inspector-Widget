# noinspection PyProtectedMember
from typing import Annotated, _AnnotatedAlias


class _MetaWidget(type):
    @staticmethod
    def _is_dunder(name):
        return name.startswith("__") and name.endswith("__")

    @staticmethod
    def _generate_new_method(class_instance, T, fields):
        def __new__(cls, label = "Name", group = "", *args, **kwargs):
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
                    print(key, "argument non existent error")

            # Store args in obj instance
            for key, value in fields.items():
                setattr(instance, key, value)

            # add 'label' and 'group' dunder members to the instance
            instance.__label__ = label
            instance.__group__ = group
            instance.__type__  = T

            # build an annotation with the args
            return Annotated[T, instance]
        return __new__

    def __new__(mcs, name, bases, members, T = None):
        # Define the new class
        class_instance = super().__new__(mcs, name, bases, members)

        complete_hierarchy = set()
        for base in bases:
            complete_hierarchy = complete_hierarchy.union(set(base.__mro__))

        fields = dict()
        for base in complete_hierarchy:
            for field_name, value in base.__dict__.items():
                if not _MetaWidget._is_dunder(field_name):
                    fields[field_name] = value

        for field_name, value in members.items():
            if not _MetaWidget._is_dunder(field_name):
                fields[field_name] = value

        class_instance.__new__ = _MetaWidget._generate_new_method(class_instance, T, fields)

        return class_instance


class Widget(metaclass=_MetaWidget):
    __label__ = ""
    __group__ = ""
    __type__ = None

    def __widget__(self, bind, default):
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
        defaults_values = type(target).__dict__  # Get all the variable names and default values of the target object reference

        for field_name, field_metadata in target.__annotations__.items():  # For each metadata blob acquired from the target
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

