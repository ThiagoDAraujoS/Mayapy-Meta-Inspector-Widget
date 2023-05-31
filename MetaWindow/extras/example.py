# noinspection PyProtectedMember
from typing import Annotated, _AnnotatedAlias
from maya import cmds
from enum import Enum
from collections import ChainMap


class UI_Color(Enum):
    """ This Enum describe some UI colors """
    RED       = 0.5,  0.1,  0.1
    GREEN     = 0.1,  0.5,  0.1
    BLUE      = 0.1,  0.3,  0.5
    YELLOW    = 0.6, 0.57,  0.2
    DARK_GRAY = 0.2,  0.2,  0.2
    PURPLE    = 0.35, 0.2,  0.6
    GRAY      = 0.3,  0.3,  0.3


class _MetaWidget(type):
    @staticmethod
    def is_dunder(name):
        return name.startswith("__") and name.endswith("__")

    @staticmethod
    def generate_new_method(class_instance, T, fields):
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
                    raise Exception(f"[ERROR] {key} non existent argument")

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

        # Collect all the fields this object has through its hierarchy
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

        # Generate a new __new__ method and pass it to the new class
        class_instance.__new__ = _MetaWidget.generate_new_method(class_instance, T, fields)

        return class_instance


class Widget(metaclass=_MetaWidget):
    __label__ = ""
    __group__ = ""
    __type__ = None

    def __widget__(self, bind, default):
        print("Abstract method invoked directly")


class _Fragment:
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

            fragment = _Fragment(target, field_name, defaults_values[field_name], instance)  # Build the reflection fragment using the metadata blob
            (fragment_groups.setdefault(fragment.data.__group__, []) if fragment.data.__group__ else ungrouped_fragments).append(fragment)  # adds it to the groups or ungroup if it has a group

        if ungrouped_fragments:  # Append the ungrouped fragments at the end of the fragment group's dictionary
            fragment_groups[""] = ungrouped_fragments
        return fragment_groups


def create_inspector_panel(ref, label_size, *args, **kwargs) -> str:
    """ Command that creates a tuning panel widget """
    root_element = cmds.columnLayout(*args, **kwargs)

    # Extract the target_ref's reflection and build frame layouts for each category
    for group_name, fragments in _Fragment.extract_reflection(ref).items():
        if group_name:
            cmds.frameLayout(l=group_name, cll=True, fn="boldLabelFont")
            cmds.columnLayout(columnAttach=('both', 0), adjustableColumn=True)

        # For each metadata fragment, build a widget for it
        for fragment in fragments:
            cmds.rowLayout(numberOfColumns=2, adjustableColumn2=2, columnWidth2=(label_size, 70), columnAlign2=["right", "left"], columnAttach2=["both", "right"])
            cmds.text(label=f"{fragment.data.__label__}", align="right", font="boldLabelFont")
            fragment.build_widget()
            cmds.setParent("..")

        cmds.separator(style="in", h=3)

        if group_name:
            cmds.setParent("..")
            cmds.setParent("..")

    cmds.setParent("..")
    return root_element


class Toggle(Widget, T=bool):
    """ label = "" \n
        group = "" \n
        true_label  = "ON" \n
        false_label = "OFF" \n
        true_color  = UI_Color.GREEN \n
        false_color = UI_Color.RED
    """
    true_label  = "ON"
    false_label = "OFF"
    true_color  = UI_Color.GREEN
    false_color = UI_Color.RED

    def __widget__(self, bind, default):
        """ Create a toggle widget """
        form_element = cmds.formLayout(numberOfDivisions=2)
        cmds.iconTextRadioCollection()
        true_element = cmds.iconTextRadioButton(
            st='textOnly', l=self.true_label, hlc=self.true_color.value, bgc=UI_Color.DARK_GRAY.value, font="smallFixedWidthFont", fla=False, select=default,
            cc=lambda value, *_: setattr(*bind, value))
        false_element = cmds.iconTextRadioButton(
            st='textOnly', l=self.false_label, hlc=self.false_color.value, bgc=UI_Color.DARK_GRAY.value, font="smallFixedWidthFont", fla=False, select=not default)

        cmds.formLayout(form_element, edit=True, attachPosition=[
            (true_element, 'top', 0, 0),  (true_element, 'bottom', 0, 2),  (true_element, 'left', 4, 0),  (true_element, 'right', 1, 1),
            (false_element, 'top', 0, 0), (false_element, 'bottom', 0, 2), (false_element, 'left', 1, 1), (false_element, 'right', 3, 2)])
        cmds.setParent("..")


class TextField(Widget, T=str):
    """ label = "" \n
        group = "" \n
    """
    def __widget__(self, bind, default):
        """ Create a text field widget """
        cmds.textField(text=default, cc=lambda value, *_: setattr(*bind, value))


class Dropdown(Widget, T=str):
    """ label = "" \n
        group = "" \n
        choices = [str]
    """
    choices = []

    def __widget__(self, bind, default):
        """ Create a text field widget """
        menu_element = cmds.optionMenu(changeCommand=lambda item, *_: setattr(*bind, item))
        for name in self.choices:
            cmds.menuItem(label=name)
        cmds.optionMenu(menu_element, edit=True, value=default)


class AbstractSlider(Widget):
    """ label = "" \n
        group = "" \n
        min = 1 \n
        max = 10
    """
    min = 1
    max = 10

    def abstract_slider(self, cmds_slider_func, cmds_field_func, bind, default) -> tuple[str, str]:
        """ Create an abstract slider widget, this method is supposed to be used through create_float_slider and create_int_slider """

        def on_update(value, *_):
            cmds_field_func(text_field_element, edit=True, value=round(float(value), 2))
            cmds_slider_func(slider_element, edit=True, value=round(float(value), 2))
            setattr(*bind, value)

        cmds.rowLayout(numberOfColumns=2, adjustableColumn2=2, columnWidth2=(35, 70), columnAlign2=["right", "left"], columnAttach2=["both", "right"])
        text_field_element = cmds_field_func(value=default, cc=on_update)
        slider_element = cmds_slider_func(value=default, min=self.min, max=self.max, cc=on_update, dc=on_update)
        cmds.setParent("..")
        return text_field_element, slider_element


class IntSlider(AbstractSlider, T=int):
    """ label = "" \n
        group = "" \n
        min = 1 \n
        max = 10
    """
    def __widget__(self, bind, default):
        super().abstract_slider(cmds.intSlider, cmds.intField, bind, default)


class FloatSlider(AbstractSlider, T=float):
    """ label = "" \n
        group = "" \n
        min = 1 \n
        max = 10
    """
    def __widget__(self, bind, default):
        text_field_element, slider_element = super().abstract_slider(cmds.floatSlider, cmds.floatField, bind, default)
        cmds.floatField(text_field_element, edit=True, tze=False, value=default)


# --------------------------EXAMPLE--------------------------------

from inspector import *
from color import *
from widgets import *


class Fruit:
    parent_j: Toggle("Parent Field", "Fruit") = False
    parent_h: TextField("Text", "Fruit") = "Bla"
    parent_k: StringBox(label="") = set()


class Banana(Fruit):
    child_a: IntSlider(label="Name", group="Fruit", min=0, max=100) = 5
    child_b: TextField("name", "Banana") = "banana banana"
    child_c: Toggle(group="Banana") = False


class Apple(Fruit):
    child_d: FloatSlider(label="Apple Slider", group="Apple", min=0, max=100) = 5
    child_f: Toggle(label="Is Pineapple", group="Apple", true_label="PINEAPPLE", false_label="APPLE", true_color=UI_Color.YELLOW, false_color=UI_Color.RED) = True


class Window:
    """ This class builds a window """
    NAME = "Test_Window"
    SIZE = 350

    def __init__(self):
        pass

    def open_window(self) -> None:
        """ Open the window """
        if cmds.window(Window.NAME, query=True, exists=True):
            cmds.deleteUI(Window.NAME, window=True)
        self.assemble_window()

    def assemble_window(self) -> str:
        """ Assemble the window, then show it """
        # Build a window element
        window_element = cmds.window(Window.NAME, sizeable=False)
        cmds.columnLayout(columnAttach=('both', 0), columnWidth=Window.SIZE + 20, )

        # Build the first Tab "Bucket tool"
        b = Banana()
        create_inspector_panel(ref=b, label_size=75, columnAttach=('both', 1), adj=True, rs=2, adjustableColumn=True)

        a = Apple()
        create_inspector_panel(ref=a, label_size=75, columnAttach=('both', 1), adj=True, rs=2, adjustableColumn=True)

        # Show the window
        cmds.showWindow(window_element)
        return window_element


w = Window()
w.open_window()
