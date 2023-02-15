_G=False;_F='left';_E=None;_D='both';_C='right';_B='..';_A=True
from typing import Annotated,_AnnotatedAlias
from maya import cmds
from enum import Enum
class UI_Color(Enum):' This Enum describe some UI colors ';RED=0.5,0.1,0.1;GREEN=0.1,0.5,0.1;BLUE=0.1,0.3,0.5;YELLOW=0.6,0.57,0.2;DARK_GRAY=0.2,0.2,0.2;PURPLE=0.35,0.2,0.6;GRAY=0.3,0.3,0.3
class _MetaWidget(type):
	@staticmethod
	def is_dunder(name):A='__';return name.startswith(A)and name.endswith(A)
	@staticmethod
	def generate_new_method(class_instance,T,members):
		def __new__(cls,label='Name',group='',*E,**F):
			A=super(class_instance,cls).__new__(cls)
			if type(A)is _AnnotatedAlias:A=A.__metadata__[0]
			C={A:B for(A,B)in members.items()if not _MetaWidget.is_dunder(A)}
			for (D,B) in zip(E,C):C[B]=D
			for (B,D) in F.items():
				if B in C:C[B]=D
				else:print('error')
			for (B,G) in C.items():setattr(A,B,G)
			A.__label__=label;A.__group__=group;A.__type__=T;return Annotated[(T,A)]
		return __new__
	def __new__(C,name,base,members,T=_E):B=members;A=super().__new__(C,name,base,B);A.__new__=_MetaWidget.generate_new_method(A,T,B);return A
class Widget(metaclass=_MetaWidget):
	__label__='';__group__='';__type__=_E
	def __widget__(A,bind,default):print('Abstract method invoked directly')
class _Fragment:
	" This class is an organized metadata info blob referred to a single variable field contained in a major object,\n Many metadata fragments account for an object's full fields meta reflection "
	def __init__(A,target_ref:object,field_name:str,default_value:object,data:Widget)->_E:(A.bind):tuple[(object,str)]=(target_ref,field_name);" The bind, represents the path to reach this variable's reference in memory, its represented by the object containing the variable and the variable's name ";(A.default):object=default_value;" This value refer to the variable's default value ";(A.data):Widget=data
	def build_widget(A):A.data.__widget__(A.bind,A.default)
	@staticmethod
	def extract_reflection(target:object)->dict[(str,list)]:
		" Extract the reflection from the target's instance and populate a dictionary of fragments ";A=target;B={};C=[];H=type(A).__dict__
		for (E,F) in A.__annotations__.items():
			if not isinstance(F,_AnnotatedAlias):continue
			G=F.__metadata__[0]
			if not issubclass(type(G),Widget):continue
			D=_Fragment(A,E,H[E],G);(B.setdefault(D.data.__group__,[])if D.data.__group__ else C).append(D)
		if C:B['']=C
		return B
def create_inspector_panel_widget(ref,label_size,*C,**D)->str:
	' Command that creates a tuning panel widget ';G='boldLabelFont';E=cmds.columnLayout(*C,**D)
	for (A,F) in _Fragment.extract_reflection(ref).items():
		if A:cmds.frameLayout(l=A,cll=_A,fn=G);cmds.columnLayout(cat=(_D,0),adj=_A)
		for B in F:cmds.rowLayout(nc=2,ad2=2,cw2=(label_size,70),cl2=[_C,_F],ct2=[_D,_C]);cmds.text(l=f"{B.data.__label__}",al=_C,fn=G);B.build_widget();cmds.setParent(_B)
		cmds.separator(st='in',h=3)
		if A:cmds.setParent(_B);cmds.setParent(_B)
	cmds.setParent(_B);return E
class Toggle(Widget,T=bool):
	' label = "" \n\ngroup = "" \n\ntrue_label = "ON" \n\nfalse_label = "OFF" \n\ntrue_color = UI_Color.GREEN \n\nfalse_color = UI_Color.RED\n';true_label='ON';false_label='OFF';true_color=UI_Color.GREEN;false_color=UI_Color.RED
	def __widget__(A,bind,default):' Create a toggle widget ';I='bottom';H='top';G='smallFixedWidthFont';F='textOnly';D=default;E=cmds.formLayout(nd=2);cmds.iconTextRadioCollection();B=cmds.iconTextRadioButton(st=F,l=A.true_label,hlc=A.true_color.value,bgc=UI_Color.DARK_GRAY.value,fn=G,fla=_G,sl=D,cc=lambda value,*A:setattr(*bind,value));C=cmds.iconTextRadioButton(st=F,l=A.false_label,hlc=A.false_color.value,bgc=UI_Color.DARK_GRAY.value,fn=G,fla=_G,sl=not D);cmds.formLayout(E,e=_A,ap=[(B,H,0,0),(B,I,0,2),(B,_F,4,0),(B,_C,1,1),(C,H,0,0),(C,I,0,2),(C,_F,1,1),(C,_C,3,2)]);cmds.setParent(_B)
class TextField(Widget,T=str):
	' label = "" \n\ngroup = "" \n\n'
	def __widget__(A,bind,default):' Create a text field widget ';cmds.textField(tx=default,cc=lambda value,*A:setattr(*bind,value))
class Dropdown(Widget,T=str):
	' label = "" \n\ngroup = "" \n\nchoices = [str]\n';choices=[]
	def __widget__(A,bind,default):
		' Create a text field widget ';B=cmds.optionMenu(cc=lambda item,*A:setattr(*bind,item))
		for C in A.choices:cmds.menuItem(l=C)
		cmds.optionMenu(B,e=_A,v=default)
class AbstractSlider(Widget):
	' label = "" \n\ngroup = "" \n\nmin = 1 \n\nmax = 10\n';min=1;max=10
	def abstract_slider(B,cmds_slider_func,cmds_field_func,bind,default)->tuple[(str,str)]:
		' Create an abstract slider widget, this method is supposed to be used through create_float_slider and create_int_slider ';E=default;D=cmds_field_func;C=cmds_slider_func
		def A(value,*B):A=value;D(F,edit=_A,value=round(float(A),2));C(G,edit=_A,value=round(float(A),2));setattr(*bind,A)
		cmds.rowLayout(nc=2,ad2=2,cw2=(35,70),cl2=[_C,_F],ct2=[_D,_C]);F=D(value=E,cc=A);G=C(value=E,min=B.min,max=B.max,cc=A,dc=A);cmds.setParent(_B);return F,G
class IntSlider(AbstractSlider,T=int):
	' label = "" \n\ngroup = "" \n\nmin = 1 \n\nmax = 10\n'
	def __widget__(A,bind,default):super().abstract_slider(cmds.intSlider,cmds.intField,bind,default)
class FloatSlider(AbstractSlider,T=float):
	' label = "" \n\ngroup = "" \n\nmin = 1 \n\nmax = 10\n'
	def __widget__(C,bind,default):A=default;B,D=super().abstract_slider(cmds.floatSlider,cmds.floatField,bind,A);cmds.floatField(B,e=_A,tze=_G,v=A)
