import inspector
from color import *
from widgets import *
from maya import cmds

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
        inspector.create_panel(ref=b, label_size=75, columnAttach=('both', 1), adj=True, rs=2, adjustableColumn=True)

        a = Apple()
        inspector.create_panel(ref=a, label_size=75, columnAttach=('both', 1), adj=True, rs=2, adjustableColumn=True)

        # Show the window
        cmds.showWindow(window_element)
        return window_element


w = Window()
w.open_window()
