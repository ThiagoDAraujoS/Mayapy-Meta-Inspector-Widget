_F=False;_E='both';_D='left';_C='..';_B='right';_A=True
from typing import Annotated,_AnnotatedAlias
from maya import cmds
from enum import Enum
from collections import ChainMap
class UI_Color(Enum):RED=0.5,0.1,0.1;GREEN=0.1,0.5,0.1;BLUE=0.1,0.3,0.5;YELLOW=0.6,0.57,0.2;DARK_GRAY=0.2,0.2,0.2;PURPLE=0.35,0.2,0.6;GRAY=0.3,0.3,0.3
class _MetaWidget(type):
	@staticmethod
	def is_dunder(name):A='__';return name.startswith(A)and name.endswith(A)
	@staticmethod
	def generate_new_method(class_instance,T,fields):
		C=fields
		def __new__(cls,label='Name',group='',*E,**F):
			A=super(class_instance,cls).__new__(cls)
			if type(A)is _AnnotatedAlias:A=A.__metadata__[0]
			for (D,B) in zip(E,C):C[B]=D
			for (B,D) in F.items():
				if B in C:C[B]=D
				else: raise Exception(f"[ERROR] {B} non existent argument")
			for (B,G) in C.items():setattr(A,B,G)
			A.__label__=label;A.__group__=group;A.__type__=T;return Annotated[(T,A)]
		return __new__
	def __new__(I,name,bases,members,T=None):
		H=members;G=bases;B=super().__new__(I,name,G,H);C=set()
		for D in G:C=C.union(set(D.__mro__))
		E=dict()
		for D in C:
			for (A,F) in D.__dict__.items():
				if not _MetaWidget.is_dunder(A):E[A]=F
		for (A,F) in H.items():
			if not _MetaWidget.is_dunder(A):E[A]=F
		B.__new__=_MetaWidget.generate_new_method(B,T,E);return B
class Widget(metaclass=_MetaWidget):
	__label__='';__group__='';__type__=None
	def __widget__(A,bind,default):print('Abstract method invoked directly')
class _Fragment:
	def __init__(A,target_ref,field_name,default_value,data):A.bind=target_ref,field_name;A.default=default_value;A.data=data
	def build_widget(A):A.data.__widget__(A.bind,A.default)
	@staticmethod
	def extract_reflection(target):
		A=target;B={};C=[];H=ChainMap(*(B.__dict__ for B in type(A).__mro__))
		for (E,F) in ChainMap(*(B.__annotations__ for B in type(A).__mro__ if'__annotations__'in B.__dict__)).items():
			if not isinstance(F,_AnnotatedAlias):continue
			G=F.__metadata__[0]
			if not issubclass(type(G),Widget):continue
			D=_Fragment(A,E,H[E],G);(B.setdefault(D.data.__group__,[])if D.data.__group__ else C).append(D)
		if C:B['']=C
		return B
def create_inspector_panel_widget(ref,label_size,*C,**D):
	G='boldLabelFont';E=cmds.columnLayout(*C,**D)
	for (A,F) in _Fragment.extract_reflection(ref).items():
		if A:cmds.frameLayout(l=A,cll=_A,fn=G);cmds.columnLayout(cat=(_E,0),adj=_A)
		for B in F:cmds.rowLayout(nc=2,ad2=2,cw2=(label_size,70),cl2=[_B,_D],ct2=[_E,_B]);cmds.text(l=f"{B.data.__label__}",al=_B,fn=G);B.build_widget();cmds.setParent(_C)
		cmds.separator(st='in',h=3)
		if A:cmds.setParent(_C);cmds.setParent(_C)
	cmds.setParent(_C);return E
class Toggle(Widget,T=bool):
	true_label='ON';false_label='OFF';true_color=UI_Color.GREEN;false_color=UI_Color.RED
	def __widget__(A,bind,default):I='bottom';H='top';G='smallFixedWidthFont';F='textOnly';D=default;E=cmds.formLayout(nd=2);cmds.iconTextRadioCollection();B=cmds.iconTextRadioButton(st=F,l=A.true_label,hlc=A.true_color.value,bgc=UI_Color.DARK_GRAY.value,fn=G,fla=_F,sl=D,cc=lambda value,*A:setattr(*bind,value));C=cmds.iconTextRadioButton(st=F,l=A.false_label,hlc=A.false_color.value,bgc=UI_Color.DARK_GRAY.value,fn=G,fla=_F,sl=not D);cmds.formLayout(E,e=_A,ap=[(B,H,0,0),(B,I,0,2),(B,_D,4,0),(B,_B,1,1),(C,H,0,0),(C,I,0,2),(C,_D,1,1),(C,_B,3,2)]);cmds.setParent(_C)
class TextField(Widget,T=str):
	def __widget__(A,bind,default):cmds.textField(tx=default,cc=lambda value,*A:setattr(*bind,value))
class Dropdown(Widget,T=str):
	choices=[]
	def __widget__(A,bind,default):
		B=cmds.optionMenu(cc=lambda item,*A:setattr(*bind,item))
		for C in A.choices:cmds.menuItem(l=C)
		cmds.optionMenu(B,e=_A,v=default)
class AbstractSlider(Widget):
	min=1;max=10
	def abstract_slider(B,cmds_slider_func,cmds_field_func,bind,default):
		E=default;D=cmds_field_func;C=cmds_slider_func
		def A(value,*B):A=value;D(F,e=_A,v=round(float(A),2));C(G,e=_A,v=round(float(A),2));setattr(*bind,A)
		cmds.rowLayout(nc=2,ad2=2,cw2=(35,70),cl2=[_B,_D],ct2=[_E,_B]);F=D(v=E,cc=A);G=C(v=E,min=B.min,max=B.max,cc=A,dc=A);cmds.setParent(_C);return F,G
class IntSlider(AbstractSlider,T=int):
	def __widget__(A,bind,default):super().abstract_slider(cmds.intSlider,cmds.intField,bind,default)
class FloatSlider(AbstractSlider,T=float):
	def __widget__(C,bind,default):A=default;B,D=super().abstract_slider(cmds.floatSlider,cmds.floatField,bind,A);cmds.floatField(B,e=_A,tze=_F,v=A)
