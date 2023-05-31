from maya import cmds
from color import *
from engine import *
from maya.api.OpenMaya import MVector
from functools import partial


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


class StringBox(Widget, T=set[str], label_style="Top"):
    selection_type = "transform"

    def __widget__(self, bind, default):
        def reset_widget(selection):
            cmds.textScrollList(main_element, edit=True, removeAll=True)
            cmds.textScrollList(main_element, edit=True, append=selection)

        def on_add_btn_press(*_):
            selection = cmds.ls(selection=True, type=self.selection_type)
            if selection:
                selection = getattr(*bind).union(selection)
                setattr(*bind, selection)
                reset_widget(selection)

        def on_del_key_press(*_):
            selection = cmds.textScrollList(main_element, query=True, selectItem=True)
            if selection:
                selection = getattr(*bind).difference(selection)
                setattr(*bind, selection)
                reset_widget(selection)

        cmds.columnLayout(adjustableColumn=True)
        main_element = cmds.textScrollList(allowMultiSelection=True, deleteKeyCommand=on_del_key_press, append=default)
        cmds.button(label="Add to List", command=on_add_btn_press)
        cmds.setParent("..")


class MVecField(Widget, T=MVector):
    def __widget__(self, bind, default):
        def on_field_edited(value, index, *_):
            getattr(*bind)[index] = value

        cmds.rowLayout(nc=3, ct3=["left", "both", "right"])
        [cmds.floatField(value=default[i], cc=partial(on_field_edited, index=i), tze=False) for i in range(3)]
        cmds.setParent("..")
