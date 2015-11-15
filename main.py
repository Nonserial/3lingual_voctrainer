from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.uix.popup import Popup
from kivy.network.urlrequest import UrlRequest
import re
import random
from settingsjson import settings_json
from kivy.base import EventLoop
from kivy.graphics import Rectangle, Color
from kivy.adapters.dictadapter import DictAdapter
from kivy.uix.listview import ListItemButton, ListItemLabel, CompositeListItem, ListView,\
    SelectableView
import os
from kivy.utils import platform
from kivy.config import ConfigParser
from kivy.uix.settings import SettingOptions, SettingSpacer
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp

# Allgemeines DateiHandling
#######################################################################################################################

class DateiHandling: # stammt 1:1 aus tkinter Dictionary
    
    # oeffnet das Dictionary und gibt es in die Variable "dictfile" aus
    def oeffnen(self, filename):
        global dateiname
        
        try:
            dataFile = open(filename, "r")
            # eval() ist notwendig, damit das Objekt den Type "dict" bekommt (ansonsten "str")
            dictfile = eval(dataFile.read())
            dataFile.close()
            return dictfile
        except:
            # falls die Datei nicht existiert, wird eine neue erzeugt
            d = open(dateiname, "w+")
            d.write("{}")
            d.close()
            # irgendwie ist das zweite oeffnen in eine andere Variable notwendig, da sonst ein Fehler auftritt??!!
            f = open(dateiname, "r")
            dict_file = eval(f.read())
            f.close()
            return dict_file
    
    def schreiben_datei(self, filename, dict_to_write):
        dataFile = open(filename, "w")
        dataFile.write(str(dict_to_write))
        dataFile.close()


# Vokabeleingabe
#######################################################################################################################

# Klasse fuer Eingabe der zu lernenden Vokabel inkl. Ueberpruefung, ob bereits vorhanden
class Input_Learn(BoxLayout):
    def __init__(self, **kwargs):
        super(Input_Learn, self).__init__(**kwargs)
        
        global i, dictlist, learn_lang, invalsettings, status
        
        status = "input"
        
        if i == 0:
            anz = Anzeige_VOCS()
            anz.open()
            
    def check_vok_in_dict(self, voc):
        global dictlist
        # checkt, ob die Vokabel bereits im Dictionary vorhanden ist
        return dictlist.__contains__(voc)
    
    def text(self):
        global learn_lang
        text = "Please type the %s word:" % learn_lang
        return text
        

    def vokabel_eingabe(self):
        global voc_learn
        
        # Auswerten des Inputs der zu lernenden Vokabel
        voc_learn = self.ids.eing_e_learn.text
        
        # If space in input use only string before space        
        if voc_learn.find(chr(32)) >=1:
            voc_learn = voc_learn[:voc_learn.find(" ")]
        elif voc_learn.find(chr(32)) == 0:
            self.ids.eing_e_learn.text = ""
            return
        elif voc_learn.find(chr(32)) == -1:
            pass
            
        
        # do nothing, if no input
        if not voc_learn:
            return
        
        self.ids.eing_e_learn.focus = False
        
        # Unerwuenschte Zeichen abfangen
        unw = Check_Unwanted()
        if unw.check(voc_learn):
            self.ids.eing_e_learn.text = ""
            return
        
        # check if voc has already been added
        if self.check_vok_in_dict(unicode(voc_learn, "utf-8")) == False:
            self.clear_widgets()
            self.add_widget(Eingabe_MOTHER_EN())
        else:
            vorh = VOC_Vorhanden()
            vorh.open()
            self.ids.eing_e_learn.text = ""
            
    def input(self):
        if self.ids.eing_e_learn.focus:
            self.do_scroll_x = False
            self.do_scroll_y = True
            self.pos = (self.width * 0.02, self.height * 0.55) if self.width < self.height else (self.height * 0.02, self.height * 0.6)
        else:
            self.pos = (self.width * 0.02, self.width * 0.02) if self.width < self.height else (self.height * 0.02, self.height * 0.02)
        return
            

# Alternative fuer Messagebox               
class VOC_Vorhanden(Popup):
    pass


# Alternative fuer Messagebox   
# Zeigt an, wie viele Vokabeln aktuell im Dictionary sind        
class Anzeige_VOCS(Popup):
    
    # Beim Klicken auf "OK" Button wird press() aufgerufen um i zu eroehen, damit verhindert wird, dass
    # vor jeder Eingabe die Anzahl der Vokabeln angezeigt wird
    def press(self):
        global i
        i += 1
        
    def lendict(self):
        global dictlist
        text = ("Your VOC-Trainer contains %s " \
                "words" % (len(dictlist))) if len(dictlist) > 1 or len(dictlist) == 0 else "Your "\
                "VOC-Trainer contains one word"
        return text
        
# Eingabe fuer Muttersprache und englische Vokabeln        
class Eingabe_MOTHER_EN(BoxLayout):
    def __init__(self, **kwargs):
        super(Eingabe_MOTHER_EN, self).__init__(**kwargs)
        
        global dictlist, voc_learn, error_count, lang_mother, lang_learn, mother_lang, learn_lang
        
        error_count = 0
        
        # Feedback if success
        self.success_mother = False
        self.success_en = False
        
        if not self.success_mother:
            self.ids.lb_ausgabe_mother.text = "searching..."
        if not self.success_en:
            self.ids.lb_ausgabe_eng.text = "searching..."
        
        self.ids.lb_wort.text = voc_learn
        
        # Template-string with format-variables
        search_template_mother = "https://glosbe.com/gapi/translate?"\
                                    "from={}&"\
                                    "dest={}&"\
                                    "format=json&"\
                                    "phrase={}&"\
                                    "pretty=true"
        search_url_mother = search_template_mother.format(lang_learn, lang_mother, voc_learn)
        #print "Search_url_mother", search_url_mother
        request_mother = UrlRequest(search_url_mother, on_success=self.search_mother_found, on_error=self.error)
        
        # Template-string with format-variables
        search_template_eng = "https://glosbe.com/gapi/translate?"\
                                    "from={}&"\
                                    "dest=eng&"\
                                    "format=json&"\
                                    "phrase={}&"\
                                    "pretty=true"
        search_url_eng = search_template_eng.format(lang_learn, voc_learn)
        #print "Search_url_eng:", search_url_eng
        request_eng = UrlRequest(search_url_eng, on_success=self.search_eng_found, on_error=self.error)
    
    def search_mother_found(self, request_mother, results):
        # Feedback, if Function has been entered
        self.success_mother = True
        
        # check if input-error
        if not results["tuc"]:
            self.not_found()
            return
        # Output-Variable
        self.ausgabe_mother = ""
        # output a maximum of 4 translations
        for i in range(4):
            try:
                results["tuc"][i]["phrase"]["text"]
            except:
                continue
            # add found translation to output-variable
            self.ausgabe_mother += results["tuc"][i]["phrase"]["text"] + ", "
            continue
        # Output in Label; caches error, if user presses the button too early
        try:
            self.ids.lb_ausgabe_mother.text = mother_lang + ":\n" + self.ausgabe_mother[:-2]
        except ReferenceError:
            return        
    
    def search_eng_found(self, request_eng, results):
        # Feedback, if Function has been entered
        self.success_en = True
        
        # check, if input-error
        if not results["tuc"]:
            self.not_found()
            return
        # Output-Variable
        self.ausgabe_eng = ""
        # output a maximum of 4 translations
        for i in range(4):
            try:
                results["tuc"][i]["phrase"]["text"]
            except:
                continue
            # add found translation to output-variable
            self.ausgabe_eng += results["tuc"][i]["phrase"]["text"] + ", "
            continue
        # Output in Label; caches error, if user presses the button too early
        try:
            self.ids.lb_ausgabe_eng.text = "English:\n" + self.ausgabe_eng[:-2]
        except ReferenceError:
            return
        
    def not_found(self):
        ntfound = NOT_Found()
        ntfound.open()
        self.clear_widgets()
        self.add_widget(Input_Learn())
    
    
    
    def add_to_dict(self):
        # if on_success has not been entered:
        if not self.success_en or not self.success_mother:
            return
            #self.clear_widgets()
            #self.add_widget(Input_Learn())
        # caches errors, when user presses the button too early
        try:         
            learn, mother, en = voc_learn, self.ausgabe_mother, self.ausgabe_eng
        except AttributeError:
            self.clear_widgets()
            self.add_widget(Input_Learn())
            return
        mother = mother[:-2]
        en = en[:-2]
        # Funktion, um Vokabeln ins Dictionary einzufuegen (zu einem Tupel konvertiert
        # und als Liste separiert mit Trennung bei den Kommata!
        dictlist[unicode(learn, "utf-8")] = (mother.encode("utf-8").split(","), en.encode("utf-8").split(","))
        
        # danach wird das aktuelle Fenster geschlossen und ein neues fuer eine weitere Vokabeleingabe geoeffnet
        self.clear_widgets()
        self.add_widget(Input_Learn())
        
    def error(self, *args):
        global error_count
        error_count += 1
        if error_count < 2:
            err = Error()
            err.open()
            self.clear_widgets()
            self.add_widget(Input_Learn())
        
        
class NOT_Found(Popup):
    pass

class Error(Popup):
    pass

# Vokabelabfrage   
#######################################################################################################################        

# Ermitteln, wie viele Vokabeln abgefrage werden sollen        
class Number_Abfragen(BoxLayout):
    def __init__(self, **kwargs):
        super(Number_Abfragen, self).__init__(**kwargs)
        
        global number, fehler, anzahl, status, abfrageliste
        
        status = "begin-abfrage"
        
        # Initialiesieren von number
        number = 0
        
        # Zaehlen der falschen Eingaben
        fehler = 0
        
        # if len(dictlist) < 3 --> get back!!
        if len(dictlist) < 3:
            status = "finish-abfrage"
            zu_klein = MSG_Klein()
            zu_klein.open()
            return
        
        # zufaellige Reihenfolge der Abfrageliste
        random.seed()
        abfrageliste = dictlist.keys()
        random.shuffle(abfrageliste)
        
    
    def anzahl(self):
        global anzahl, dictlist
        
        if not self.ids.abfr_eingabe.text:
            return
        
        self.ids.abfr_eingabe.focus = False
        
        # Speichert Anzahl an abzufragenden Vokabeln in Variabel anzahl
        anzahl = self.ids.abfr_eingabe.text
        
        # testen ob gueltige Eingabe
        try:
            anzahl = int(anzahl)
            if anzahl > len(dictlist) or anzahl < 3:
                raise
        except:
            ung = Ungueltig()
            ung.open()
            self.ids.abfr_eingabe.text = ""
            return # wichtig, da sonst Funktion weiterlaeuft und Fehler gibt
            
        self.clear_widgets()
        self.add_widget(Abfrage())
        
    def input(self):
        if self.ids.abfr_eingabe.focus:
            self.do_scroll_x = False
            self.do_scroll_y = True
            self.pos = (self.width * 0.02, self.height * 0.55) if self.width < self.height else (self.height * 0.02, self.height * 0.6)
        else:
            self.pos = (self.width * 0.02, self.width * 0.02) if self.width < self.height else (self.height * 0.02, self.height * 0.02)
        return
            
            
# Exception, falls Number_Abfragen keine gueltige Zahl ergibt            
class Ungueltig(Popup):
    def lb_text(self):
        text = self.ids.lb_ungueltig.text = "Please insert a valid number between '3' and "\
                                       "'%i'." % (len(dictlist))
        return text
            

class Abfrage(BoxLayout):
    
    def __init__(self, **kwargs):
        super(Abfrage, self).__init__(**kwargs)
        
        global dictlist, number, anzahl, fehler, mother_lang, abfrageliste, \
        mother, en, answ_en, answ_pos_list_en, voc_learn, status, durchlauf
        
        status = "abfrage"
        
        if durchlauf == 0:
         
            # Initialisieren
            mother, en = None, None
            voc_learn = None
            
            # Muttersprache:
            self.ids.abfr_lb_language.text = "%s translation:" % mother_lang
            
            
            # Vokabelabfrage, so lange bis ausgewaehlte Anzahl erreicht ist
            if number < anzahl:
                for element in range(0, anzahl):       
                    voc_learn = abfrageliste[number]
                    self.ids.abfr_lb_wort.text = voc_learn
            elif number == anzahl:
                # Keine weiteren Vokabeln mehr
                self.clear_widgets()
                no_vocs = Factory.No_VOCS() 
                no_vocs.open()
                status = "finish-abfrage"
                return
            
        
            # Speichern der richtigen Loesungen fuer diesen Durchgang
            mother, en = dictlist[voc_learn]      
    
            # korrekte Umwandlung der Liste in unicode
            liste = []
            for element in mother:
                liste.append(unicode(element, "utf-8"))
            mother = liste
            
            liste = []
            for element in en:
                liste.append(unicode(element, "utf-8"))
            en = liste
        
            # Schreiben der Antwortmoeglichkeiten Muttersprache muss hier passieren:
            # richtige Antwort Mutter:
            answ_mother = self.antw_beschneiden(mother)
            
            # richtige Antwort Englisch:
            answ_en = self.antw_beschneiden(en)
            
            # Antwortmoeglichkeiten in Muttersprache:        
            # alle moegliche Antworten
            # Copy des Dicts notwendig, da sonst dictionary veraendert wird
            answ_pos_list = dictlist.copy()
    
            # entferne gesuchtes Wort aus Antwortmoeglichkeiten
            answ_pos_list.pop(voc_learn, None)
        
            # aufdroeseln der Antworten in Muttersprache und Englisch
            answ_pos_list_mother = []
            answ_pos_list_en = []
            for i in answ_pos_list.values():
                m, e = i
                answ_pos_list_mother.append(m)
                answ_pos_list_en.append(e)
            random.seed()
            random.shuffle(answ_pos_list_mother)
            random.shuffle(answ_pos_list_en)
    
        
            # Beschneiden der Antwortmoeglichkeiten:
            x = []
            for i in answ_pos_list_mother:
                a = self.antw_beschneiden(i)
                x.append(a)
            
            answ_pos_list_mother = x
            
            x = []
            for i in answ_pos_list_en:
                a = self.antw_beschneiden(i)
                x.append(a)
                
            answ_pos_list_en = x
        
            random.seed()
            random.shuffle(answ_pos_list_mother)
            
            random.seed()
            random.shuffle(answ_pos_list_en)
            
            # schreiben der Muttersprachen-Antworten in Labels:
            self.antw_text(answ_mother, answ_pos_list_mother[0], answ_pos_list_mother[1])    
        
        
        elif durchlauf == 1:
            self.ids.abfr_lb_wort.text = voc_learn
            self.ids.abfr_lb_language.text = "English translation:"
            self.antw_text(answ_en, answ_pos_list_en[0], answ_pos_list_en[1])
            
        
    def antw_text(self, eins, zwei, drei):
        random.seed()
        rand_list = [eins, zwei, drei]
        random.shuffle(rand_list)
        
        self.ids.answer_1.text = "[ref=eins]" + ",".join(rand_list[0]) + "[/ref]"
        self.ids.answer_2.text = "[ref=zwei]" + ",".join(rand_list[1]) + "[/ref]"
        self.ids.answer_3.text = "[ref=drei]" + ",".join(rand_list[2]) + "[/ref]"
        return

    def antw_beschneiden(self, antwort):        
        # max. Anzahl der angezeigten Antworten = 3
        # Antwortmoeglichkeiten Muttersprache
        if len(antwort) < 3:
            return antwort
        else:
            return antwort[:3]
        
        # Antwortmoeglichkeiten Englisch    
        if len(en) < 3:
            answ_en = en
        else:
            answ_en = en[:3]
            
    def get_antw(self, checkbox):
        try:
            if checkbox == 1:
                answer = self.ids.answer_1.text
            elif checkbox == 2:
                answer = self.ids.answer_2.text
            elif checkbox == 3:
                answer = self.ids.answer_3.text
            return answer.split(",")
        except:
            return
        
    def activatecb(self, cb):
        if cb == 1:
            self.ids.eins.active = True
            self.ids.zwei.active = False
            self.ids.drei.active = False
        elif cb == 2:
            self.ids.zwei.active = True
            self.ids.eins.active = False
            self.ids.drei.active = False
        elif cb == 3:
            self.ids.drei.active = True
            self.ids.eins.active = False
            self.ids.zwei.active = False
        
            
    def pruefen(self, checkbox):
        global number, fehler, mother, en, durchlauf
        
        answer = self.get_antw(checkbox)     
        
        # loescht "[/ref]" aus Antwort und faengt Fehler ab
        try:
            if len(answer) == 1:
                answer = answer[0][:-6]
        except TypeError:
            return
        
        if durchlauf == 0:
            # Checke Muttersprache:
            # "answer[0][10:]" notwendig; loescht "[ref=...]" aus Antwort
            if any(answer[0][10:] in s for s in mother):
                durchlauf = 1
                gut = MSG_Richtig_DE()
                gut.open()  
                self.clear_widgets()              
                self.add_widget(Abfrage())
            else:
                wro = MSG_Fehler()
                wro.open()
            
        elif durchlauf == 1:
            # Checke Englisch:      
            if any(answer[0][10:] in s for s in en):
                number += 1
                durchlauf = 0
                gut = MSG_Richtig_EN()
                gut.open()  
            else:
                wro = MSG_Fehler()
                wro.open()
        return   
        
    def wert_uebergabe(self):
        wert = 0
        if self.ids.eins.active == True:
            wert = 1
        elif self.ids.zwei.active == True:
            wert = 2
        elif self.ids.drei.active == True:
            wert = 3
        return wert
    
    def back(self):
        global status
        status = "finish-abfrage"

        
# Alternative fuer Messagebox        
class MSG_Fehler(Popup):
    pass

class MSG_Richtig_DE(Popup):
    pass
         
class MSG_Richtig_EN(Popup):
    pass

class MSG_Klein(Popup):
    pass
   
        
# Liste des Dictionarys anzeigen lassen        
#######################################################################################################################  
class List(BoxLayout):
    def __init__(self, **kwargs):
        kwargs["cols"] = 1
        super(List, self).__init__(**kwargs)

        global dictlist, status, liste_dict
        
        status = "list"
        
        args_converter = \
            lambda row_index, rec: \
            {"text": rec["text"],
             "size_hint_y": None,
             "heigth": 25}
        
        liste = []
        for element in sorted(dictlist.keys()):
            liste.append(element.encode("utf-8"))

        liste_dict = {str(i): {"text": str(i), "is_selected": False} for i in liste} #dictlist.keys())} 
        
        '''dict_adapter = DictAdapter(#sorted_keys = keys_sorted,
                                   args_converter = args_converter,
                                   data = liste_dict,
                                   selection_mode = "single",
                                   allow_empty_selection = False,
                                   cls = ListItemButton) #CompositeListItem)'''
        
        dict_adapter = Adapter(args_converter = args_converter, data = liste_dict, cls = ListItemButton)
        list_view = ListView(adapter=dict_adapter)
        self.ids.list_liste.add_widget(list_view)

    
        
class Adapter(DictAdapter):
    def __init__(self, **kwargs):
        super(Adapter, self).__init__(**kwargs)
        
        global voc_learn, dictlist, liste_dict
        self.propagate_selection_to_data = True
        self.selection_mode = "single"
        
        try:
            voc_learn
            liste_dict[sorted(dictlist.keys())[0].encode("utf-8")]["is_selected"] = False
            #self.select_item_view(SelectableView)
        except NameError:
            voc_learn = sorted(dictlist.keys())[0].encode("utf-8")
        liste_dict[voc_learn]["is_selected"] = True

        
    def on_selection_change(self, *args):
        DictAdapter.on_selection_change(self, *args)
        global voc_learn

        for i in self.selection:
            voc_learn = i.text

                
class Edit(BoxLayout):
    def __init__(self, **kwargs):
        super(Edit, self).__init__(**kwargs)
        global edit_learn, edit_mother, edit_en, search, learn_lang, mother_lang, dictlist
        self.ids.eing_edit_learn.text = edit_learn
        self.ids.eing_edit_mother.text = edit_mother
        self.ids.eing_edit_en.text = edit_en
        
    def input(self):
        if self.ids.eing_edit_learn.focus:
            self.do_scroll_x = False
            self.do_scroll_y = True
            self.pos = (self.width * 0.02, self.height * 0.2) if self.width < self.height else (self.height * 0.02, self.height * 0.1)
        elif self.ids.eing_edit_mother.focus:
            self.do_scroll_x = False
            self.do_scroll_y = True
            self.pos = (self.width * 0.02, self.height * 0.37) if self.width < self.height else (self.height * 0.02, self.height * 0.35)
        elif self.ids.eing_edit_en.focus:
            self.do_scroll_x = False
            self.do_scroll_y = True
            self.pos = (self.width * 0.02, self.height * 0.55) if self.width < self.height else (self.height * 0.02, self.height * 0.6)
        else:
            self.pos = (self.width * 0.02, self.width * 0.02) if self.width < self.height else (self.height * 0.02, self.height * 0.02)
        return
    
    def edit(self):
        if search == unicode(self.ids.eing_edit_learn.text, "utf-8"):
            if edit_mother == unicode(self.ids.eing_edit_mother.text, "utf-8"):
                if edit_en == unicode(self.ids.eing_edit_en.text, "utf-8"):
                    return
        # unerwuenschte Zeichen abfangen
        zeichen = self.ids.eing_edit_learn.text + self.ids.eing_edit_mother.text + self.ids.eing_edit_en.text
        
        unw = Check_Unwanted()
        if unw.check(zeichen):
            self.ids.eing_edit_mother.text = ",".join(dictlist[search][0])
            self.ids.eing_edit_en.text = ",".join(dictlist[search][1])
            return
        
        del dictlist[search]
        dictlist[unicode(self.ids.eing_edit_learn.text, "utf-8")] = (unicode(self.ids.eing_edit_mother.text, "utf-8").split(","), unicode(self.ids.eing_edit_en.text, "utf-8").split(","))
    
        save = MSG_Save()
        save.open()
        
        
    def text(self, lang):
        if lang == "learn":
            return "%s: " % learn_lang
        elif lang == "mother":
            return "%s: " % mother_lang
        elif lang == "en":
            return "English:"
        
        
    
class MSG_Save(Popup):
    pass

# Check if unwanted characters
#######################################################################################################################        

class Check_Unwanted:
    def check(self, string):
        global unerwuenscht
        if re.search(unerwuenscht, string):
            uner = Unerwuenscht()
            uner.open()
            return True
        return False
        

class Unerwuenscht(Popup):
    def unwanted(self):
        text = "Your input contains an unwanted character: \n"\
        "%s \n\n" \
        "Please check and repeat your input!" % unerwuenscht
        return text
    
        
# Backup des Dictionary erstellen        
#######################################################################################################################        
### Backup erstellen
class Backup:
    def __init__(self):
        global dictlist, dateiname
        bu = DateiHandling()
        if platform == "android":
            bu.schreiben_datei("/storage/emulated/0/backups/voctrainer/" + dateiname, dictlist)
        else:    
            bu.schreiben_datei("../backups/voctrainer/" + dateiname, dictlist)
        #tkinter.messagebox.showinfo("Backup", "Eine Sicherungskopie des Dictionarys wurde unter dem Dateinamen 'dict-backup.txt' angelegt.")        

# Hauptklassen usw.        
#######################################################################################################################      
        
# RootKlasse des Programms        
class DictionaryRoot(BoxLayout):
    
    def __init__(self, **kwargs):
        super (DictionaryRoot, self).__init__(**kwargs)
        global invalsettings, dictlist, voc_learn
        try:
            del voc_learn
        except:
            return
    
    def eingabe_form(self):
        if invalsettings:
            inval = MSG_Invalid_Settings()
            inval.open()
            return
        self.clear_widgets()
        self.add_widget(Input_Learn())
        
    def abfrage_form(self):
        if invalsettings:
            inval = MSG_Invalid_Settings()
            inval.open()
            return
        if not dictlist:
            return
        self.clear_widgets()
        self.add_widget(Number_Abfragen())
    
    def list(self):
        if invalsettings:
            inval = MSG_Invalid_Settings()
            inval.open()
            return
        if not dictlist:
            return
        self.clear_widgets()
        self.add_widget(List())
        
        
        
class MSG_Invalid_Settings(Popup):
    pass


# ScrollOptions for settings Popup
class SettingScrollOptions(SettingOptions):
    
    def _create_popup(self, instance):
        # create the popup
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
            content=content, title=self.title, size_hint=(None, None),
            size=(popup_width, '400dp'))
        
        ## kommentiere popup.height aus, um Hoehe zu kontrolliereni
        #popup.height = len(self.options) * dp(55) + dp(150)

        # add all the options
        content.add_widget(Widget(size_hint_y=None, height=1))
        uid = str(self.uid)
        for option in self.options:
            state = 'down' if option == self.value else 'normal'
            btn = ToggleButton(text=option, state=state, group=uid)
            btn.bind(on_release=self._set_option)
            content.add_widget(btn)

        # finally, add a cancel button to return on the previous panel
        content.add_widget(SettingSpacer())
        btn = Button(text='Cancel', size_hint_y=None, height=dp(50))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)

        # and open the popup !
        popup.open()


# App-Klasse des Programms (Herzstueck)
class DictionaryApp(App):
    
    def __init__(self, **kwargs):
        super(DictionaryApp, self).__init__(**kwargs)
        global i, unerwuenscht, invalsettings, status, durchlauf, z
        
        invalsettings = True
        
        self.config = ConfigParser()
        
        # Zaehler um anzuzueigen, wie viele Vokabeln in Dict
        i = 0
        
        status = "main"
        
        # Abfragedurchlauf Initialisieren
        anzahl = "0"
        durchlauf = 0
                
        # unerwuenschte Zeichen
        unerwuenscht = "[(?!:;.1234567890)+-]"
        
        # switch off Kivy_settings
        self.use_kivy_settings = False
        
        # Directory for Backups
        if platform == "android":
            self.bu_pfad = "/storage/emulated/0/backups/voctrainer/"
            #self.bu_pfad = "../../backups/voctrainer"
            if not os.path.exists(self.bu_pfad):
                os.makedirs(self.bu_pfad)
        else:
            self.bu_pfad = "../backups/voctrainer/"
            if not os.path.exists(self.bu_pfad):
                os.makedirs(self.bu_pfad)
        
        
    def build(self):
        self.root = DictionaryRoot()
        
        # init the variables for search-query
        self.take_from_build_away()
        
        self.title = "Voc-Trainer"
        return self.root
    
    # this needs to be separated from def build(); otherwise you get problems when running
    # from def on_config_change()
    def take_from_build_away(self):
        global learn_lang, mother_lang, lang_learn, lang_mother, invalsettings, dictlist, dateiname, ersatz_pfad
        
        # capture error on android
        self.build_config(self.config)
        
        # get values from settingsmenu
        learn_lang = self.config.get("languages", "learnlanguage")
        mother_lang = self.config.get("languages", "motherlanguage")
       
        ## load backupfile
        try:
            # dateiname bei erstem durchlauf noch nicht konfiguriert --> Error
            # check language of backupfile
            if not ersatz_pfad[ersatz_pfad.find("VOC_TR_"):] == dateiname:
                raise
            # get data in backupfile
            open_dict = DateiHandling()
            # overwrite global variable dictlist
            dictlist = open_dict.oeffnen(ersatz_pfad)
            open_dict.schreiben_datei(dateiname, dictlist)
            ersatz_pfad = ""
            # reset backuppath
        except:
            pass
        
        # reset backuppath
        try:
            self.config.read("dictionary.ini")
            # reset path
            self.config.set("languages", "backuppath", self.bu_pfad)
        except:
            pass
        
        # exception handler neccessary because of opening app after having made
        # backup causes issues
        try:
            if self.config.get("languages", "makebackup") == "yes" and len(dictlist) != 0:
                Backup()       
        except:
            pass
        
        # reset settings
        self.config.set("languages", "makebackup", "no")
        
        # get varibles for search-query
        lang_learn, lang_mother = self.init_variables(learn_lang, mother_lang)

        # check invalide settings
        self.check_inval_settings()
        if not invalsettings:
            # open the requested file, if exists; otherwise create it
            self.load_dictionary()
    
    def load_dictionary(self):
        global dictlist, lang_learn, lang_mother, dateiname
        # Dictionary importieren und in der Variablen "dictlist" ablegen
        open_dict = DateiHandling()
        dateiname = str("VOC_TR_" + lang_learn + "-" + lang_mother + ".txt")
        #print "Open file:", dateiname
        dictlist = open_dict.oeffnen(dateiname)
        
    
    # config-preset for our own settings:
    def build_config(self, config):
        try:
            config.read("dictionary.ini")
            config.set("languages", "backuppath", self.bu_pfad)
        except:
            config.setdefaults(
                           "languages", {
                                         "learnlanguage": "Italian",
                                         "motherlanguage": "German",
                                         "backuppath": "../backups/voctrainer/",
                                         "makebackup": 0}
                               )
    
    # add our own settings:
    def build_settings(self, settings):
        settings.register_type("scrolloptions", SettingScrollOptions)
        settings.add_json_panel("VOC-Trainer Settings", self.config, data = settings_json)
        
    # change variables on settings-change
    def on_config_change(self, config, section, key, value):
        global invalsettings, ersatz_pfad
        # ersatzpfad notwendig, da neuer build_config durchlauf in take_from_build_away
        ersatz_pfad = self.config.get("languages", "backuppath")
        self.root.clear_widgets()
        self.root.canvas.clear() # sonst Fehler mit Hintergrundfarbe
        self.root.padding = 0 # sonst Fehler; btw tritt immer noch auf
        self.check_inval_settings()
        self.root.add_widget(DictionaryRoot())
        if not invalsettings:
            self.take_from_build_away()
        else:
            return
    
    def check_inval_settings(self):
        global invalsettings
        if self.config.get("languages", "learnlanguage") == self.config.get("languages", "motherlanguage"):
            invalsettings = True
        else:
            invalsettings = False        
        
    def init_variables(self, learn_lang, mother_lang):
        # initialize lang_learn depending on settings
        lang_learn = self.select_lang(learn_lang)
        lang_mother = self.select_lang(mother_lang)
        return lang_learn, lang_mother
    
    def select_lang(self, language):
        # ita - Italian
        # de - German
        # fra - French
        # es - Spanish
        # ru - Russian
        # ro - Romanian
        # tr - Turkish
        # ar - Arabic
        if language == "Arabic":
            lang = "ar"
        elif language == "French":
            lang = "fra"
        elif language == "German":
            lang = "deu"
        elif language == "Italian":
            lang = "ita"
        elif language == "Romanian":
            lang = "ro"
        elif language == "Russian":
            lang = "ru"
        elif language == "Spanish":
            lang = "es"
        elif language == "Turkish":
            lang = "tr"        
        return lang
    
    
    def back(self):
        # setzt i fuer Anzeige der Anzahl der Vokabeln zurueck
        
        global i, dateiname, status
        #### hier muss das Dictionary gespeichert werden ####
        write_dict = DateiHandling()
        # das funktioniert, weil diclist.append nur aufgerufen wird, wenn auch muttersprache und englische Vokabel eingegeben wurde!!!
        # ansonsten ist dictlist unveraendert
        write_dict.schreiben_datei(dateiname, dictlist)
        # damit man wieder zum Input zurueck kommt, wenn show von dort aufgerufen wird
        if status == "from_input":
            self.root.clear_widgets()
            self.root.canvas.clear() # sonst Fehler mit Hintergrundfarbe
            self.root.padding = 0 # sonst Fehler
            #self.root.canvas.add(Color(0.5, 0.5, 1, 0.5))
            #self.root.canvas.add(Rectangle(size = self.root.size, pos = self.root.pos))
            self.root.padding = (self.root.width * 0.02, self.root.width * 0.02) if self.root.width < self.root.height else (self.root.height * 0.02, self.root.height * 0.02)
            self.root.add_widget(Input_Learn())
        elif status == "from_list":
            self.root.clear_widgets()
            self.root.canvas.clear() # sonst Fehler mit Hintergrundfarbe
            self.root.padding = 0 # sonst Fehler
            self.root.padding = (self.root.width * 0.02, self.root.width * 0.02) if self.root.width < self.root.height else (self.root.height * 0.02, self.root.height * 0.02)
            self.root.add_widget(List())
        elif status == "abfrage":
            self.root.clear_widgets()
            self.root.canvas.clear() # sonst Fehler mit Hintergrundfarbe
            self.root.padding = 0 # sonst Fehler
            self.root.padding = (self.root.width * 0.02, self.root.width * 0.02) if self.root.width < self.root.height else (self.root.height * 0.02, self.root.height * 0.02)
            self.root.add_widget(Abfrage())
            return
        else:
            # Zuruecksetzen des Zaehlers, damit beim erneuten Aufruf wieder die Anzahl der Vokabeln im Dictionary angezeigt wird
            i = 0
            status = "main"
            self.root.clear_widgets()
            self.root.canvas.clear() # sonst Fehler mit Hintergrundfarbe
            self.root.padding = 0 # sonst Fehler
            self.root.add_widget(DictionaryRoot())
        
        
    def show(self):
        global voc_learn, edit_learn, edit_mother, edit_en, search, status
       
        if status == "input":
            status = "from_input"
        elif status == "list":
            status = "from_list"
            
        search = unicode(voc_learn, "utf-8")
        edit_learn = search
        edit_mother = ",".join(dictlist[search][0])
        edit_en = ",".join(dictlist[search][1])
        self.root.clear_widgets()
        self.root.canvas.clear() # sonst Fehler mit Hintergrundfarbe
        self.root.padding = 0 # sonst Fehler
        #self.root.canvas.add(Color(0.5, 0.5, 1, 0.5))
        #self.root.canvas.add(Rectangle(size = self.root.size, pos = self.root.pos))
        self.root.padding = (self.root.width * 0.02, self.root.width * 0.02) if self.root.width < self.root.height else (self.root.height * 0.02, self.root.height * 0.02)
        self.root.add_widget(Edit())
        
    def on_pause(self):
        return True
    
    def on_resume(self):
        pass
    
    # changes the function of the "back" button aka. "esc" to not throw you out of application 
    # when not in main-menu
    def on_start(self):
        EventLoop.window.bind(on_keyboard=self.checkback)
        
    # checks every key-event if esc-button
    def checkback(self, window, key, *args):
        if key == 27:
            if status != "main":
                self.back()
                return True
            else:
                return False
        return


# MainLoop
if __name__ == "__main__":
    status = "main"
    DictionaryApp().run()
    
# TODO: Backupfunktion ins Settings