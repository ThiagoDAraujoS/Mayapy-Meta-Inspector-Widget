# noinspection PyProtectedMember
from typing import Annotated, _AnnotatedAlias
from collections import ChainMap


class _MetaWidget(type):
    """ Hidden widget's class factory """

    @staticmethod
    def is_dunder(name):
        """ Verify if this field name is a double underscored """
        return name.startswith("__") and name.endswith("__")

    @staticmethod
    def generate_new_method(class_instance, T, fields):
        """ Generate a new __new__ method for this class """

        # Define the new __new__ method
        def __new__(cls, label = "Name", group = "", *args, **kwargs):

            # Create a widget meta-blob instance
            instance = super(class_instance, cls).__new__(cls)
            if type(instance) is _AnnotatedAlias:
                instance = instance.__metadata__[0]

            # Edit the fields dictionary by replacing its values by the __init__ args and kwargs
            # Update its default members in order using the *args list
            for arg, key in zip(args, fields):
                fields[key] = arg

            # Update its default members by using the **kwargs keys
            for key, arg in kwargs.items():
                # if the key exists update it
                if key in fields:
                    fields[key] = arg

                # if no throw an error
                else:
                    raise Exception(f"[ERROR] {key} non existent argument")

            # move all the field's values onto the instance obj
            for key, value in fields.items():
                setattr(instance, key, value)

            # add 'label' and 'group' dunder members to the instance
            instance.__label__ = label
            instance.__group__ = group
            instance.__type__  = T

            # build an annotation with the args then allocate the meta-blob into its first slot
            return Annotated[T, instance]

        # return the generated __new__ method
        return __new__

    def __new__(mcs, name, bases, members, T = None):
        """ Create this new widget class instance """

        # Create a new empty class child of bases
        class_instance = super().__new__(mcs, name, bases, members)

        # collect the class's complete hierarchy
        complete_hierarchy = set()
        for base in bases:
            complete_hierarchy = complete_hierarchy.union(set(base.__mro__))

        # collect this class parent fields as a dictionary
        fields = dict()
        for base in complete_hierarchy:
            for field_name, value in base.__dict__.items():
                if not _MetaWidget.is_dunder(field_name):
                    fields[field_name] = value

        # Include this class' fields to the fields dictionary
        for field_name, value in members.items():
            if not _MetaWidget.is_dunder(field_name):
                fields[field_name] = value

        # Generate a new __new__ method using the collected fields, and widget's inspected datatype
        class_instance.__new__ = _MetaWidget.generate_new_method(class_instance, T, fields)

        # return this new class
        return class_instance


class Widget(metaclass=_MetaWidget):
    """ Base widget class """

    __label__ = ""
    """ Widget's label text"""

    __group__ = ""
    """ Widget's group name"""

    __type__ = None
    """ Widget's tracked data type """

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
        """ The metadata blob contained within this fragment's annotation """

    def build_widget(self):
        self.data.__widget__(self.bind, self.default)

    @staticmethod
    def extract_reflection(target: object) -> dict[str, list]:
        """ Extract the reflection from the target's instance and populate a dictionary of fragments """
        fragment_groups = {}
        ungrouped_fragments = []
        defaults_values = ChainMap(*(c.__dict__ for c in type(target).__mro__))

        # For each metadata blob acquired from the target
        for field_name, field_metadata in ChainMap(*(c.__annotations__ for c in type(target).__mro__ if '__annotations__' in c.__dict__)).items():

            # Check if the field meta stub is an Annotation object
            if not isinstance(field_metadata, _AnnotatedAlias):
                continue

            # Check if the Annotation's first meta blob is child of a Widget obj
            instance = field_metadata.__metadata__[0]
            if not issubclass(type(instance), Widget):
                continue

            # Build the reflection fragment using the metadata blob
            fragment = Fragment(target, field_name, defaults_values[field_name], instance)

            # adds it to the groups or ungroup if it has a group
            (fragment_groups.setdefault(fragment.data.__group__, []) if fragment.data.__group__ else ungrouped_fragments).append(fragment)

        # Append the ungrouped fragments at the end of the fragment group's dictionary
        if ungrouped_fragments:
            fragment_groups[""] = ungrouped_fragments
        return fragment_groups

