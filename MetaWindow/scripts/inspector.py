from widgets import *
from engine import *
from maya import cmds


# def create_inspector_panel(ref, label_size, *args, **kwargs) -> str:
#     """ Command that creates a tuning panel widget """
#     root_element = cmds.columnLayout(*args, **kwargs)
#
#     # Extract the target_ref's reflection and build frame layouts for each category
#     for group_name, fragments in Fragment.extract_reflection(ref).items():
#         if group_name:
#             cmds.frameLayout(l=group_name, cll=True, fn="boldLabelFont")
#             cmds.columnLayout(columnAttach=('both', 0), adjustableColumn=True)
#
#         # For each metadata fragment, build a widget for it
#         for fragment in fragments:
#             cmds.rowLayout(numberOfColumns=2, adjustableColumn2=2, columnWidth2=(label_size, 70), columnAlign2=["right", "left"], columnAttach2=["both", "right"])
#             cmds.text(label=f"{fragment.data.__label__}", align="right", font="boldLabelFont")
#             fragment.build_widget()
#             cmds.setParent("..")
#
#         cmds.separator(style="in", h=3)
#
#         if group_name:
#             cmds.setParent("..")
#             cmds.setParent("..")
#
#     cmds.setParent("..")
#     return root_element


def create_inspector_panel(ref, label_size, *args, **kwargs) -> str:
    """ Command that creates a tuning panel widget """
    root_element = cmds.columnLayout(*args, **kwargs)

    # Extract the target_ref's reflection and build frame layouts for each category
    for group_name, fragments in Fragment.extract_reflection(ref).items():
        if group_name:
            cmds.frameLayout(l=group_name, cll=True, fn="boldLabelFont")
            cmds.columnLayout(columnAttach=('both', 0), adjustableColumn=True)

        # For each metadata fragment, build a widget for it
        for fragment in fragments:
            if fragment.data.__label__:
                if fragment.data.__label_style__ == LabelStyle.Left:
                    cmds.rowLayout(numberOfColumns=2, adjustableColumn2=2, columnWidth2=(label_size, 70), columnAlign2=["right", "left"], columnAttach2=["both", "right"])
                    cmds.text(label=f"{fragment.data.__label__.title()}:", align="right", font="boldLabelFont")
                    fragment.build_widget()
                    cmds.setParent("..")

                elif fragment.data.__label_style__ == LabelStyle.Top:
                    cmds.columnLayout(adj=True)
                    cmds.text(label=f"{fragment.data.__label__.title()}:", align="left", font="boldLabelFont")
                    fragment.build_widget()
                    cmds.setParent("..")
            elif not fragment.data.__label__ or fragment.data.__label_style__ == LabelStyle.Off:
                fragment.build_widget()

        cmds.separator(style="in", h=3)

        if group_name:
            cmds.setParent("..")
            cmds.setParent("..")

    cmds.setParent("..")
    return root_element
