from gluon.sqlhtml import *

jqueryui_content = "ui-widget ui-widget-content ui-corner-all"
jqueryui_header = "ui-widget ui-widget-header ui-corner-all"

class CKEditorWidget(FormWidget):
    @staticmethod
    def widget(field, value, **attributes):
        return TEXTAREA(_id = str(field).replace('.','_'), _name=field.name, _class='text', value=value)

class HiddenWidget(FormWidget):

    @staticmethod
    def widget(field, value, **attributes):
        """
        generates an INPUT text tag.

        see also: :meth:`FormWidget.widget`
        """

        default = dict(
            _type = 'hidden',
            value = (value!=None and str(value)) or '',
            )
        attr = StringWidget._attributes(field, default, **attributes)

        return INPUT(**attr)
        
class UIStringWidget(StringWidget):
    @staticmethod
    def widget(field, value, **attributes):        
        return StringWidget.widget(field, value, _class=jqueryui_content, **attributes)
   
class UIPasswordWidget(PasswordWidget):
    @staticmethod
    def widget(field, value, **attributes):        
        return PasswordWidget.widget(field, value, _class=jqueryui_content, **attributes)
        
class UITextWidget(TextWidget):
    @staticmethod
    def widget(f, v, **k):
        return TextWidget.widget(f, v, _class=jqueryui_content, **k)
        
class UIOptionsWidget(OptionsWidget):
    @staticmethod
    def widget(f, v, **k):
        return OptionsWidget.widget(f, v, _class=jqueryui_header, **k)
        
class WMD_IGNORE(TextWidget):
    @staticmethod
    def widget(f, v, **k):
        return TextWidget.widget(f, v, _class='text wmd-ignore', **k)
        
class WMD_PREVIEW(TextWidget):
    @staticmethod
    def widget(f, v, **k):
        return TextWidget.widget(f, v, _class='text wmd-preview', **k)
        
class WMD_OUTPUT(TextWidget):
    @staticmethod
    def widget(f, v, **k):
        return TextWidget.widget(f, v, _class='text wmd-output', **k)
        
class RESIZABLE(TextWidget):
    @staticmethod
    def widget(f, v, **k):
        return TextWidget.widget(f, v, _class='text resizable', **k)
    

SQLFORM.widgets.string = UIStringWidget
SQLFORM.widgets.text = UITextWidget
SQLFORM.widgets.options = UIOptionsWidget
SQLFORM.widgets.password = UIPasswordWidget
        
        
#        password = PasswordWidget,
#        integer = IntegerWidget,
#        double = DoubleWidget,
#        time = TimeWidget,
#        date = DateWidget,
#        datetime = DatetimeWidget,
#        upload = UploadWidget,
#        boolean = BooleanWidget,
#        blob = None,
#        multiple = MultipleOptionsWidget,
#        radio = RadioWidget,
#        checkboxes = CheckboxesWidget,
