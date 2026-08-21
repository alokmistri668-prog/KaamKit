from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'system')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform
import datetime
import math
import os
import re

THEME = {
    "is_dark": True,
    "bg": (0.05, 0.07, 0.10, 1),
    "card_bg": (0.10, 0.13, 0.18, 1),
    "header_bg": (0.10, 0.14, 0.20, 1),
    "text": (0.95, 0.96, 1.0, 1),
    "sub_text": (0.65, 0.75, 0.85, 1),
    "highlight": (0.1, 0.4, 0.8, 1), 
    "result": (0.3, 0.9, 0.5, 1), 
    "warn": (1.0, 0.7, 0.2, 1), 
    "input_bg": (0.15, 0.20, 0.28, 1),
    "input_fg": (1.0, 1.0, 1.0, 1),
    "btn_bg": (0.18, 0.24, 0.35, 1),
    "btn_active": (0.1, 0.4, 0.8, 1),
    "btn_inactive": (0.18, 0.24, 0.35, 1),
    "back_btn_bg": (0.1, 0.45, 0.85, 1),
    "calc_bg": (0.05, 0.07, 0.10, 1),
    "calc_text": (1.0, 1.0, 1.0, 1),
    "calc_result": (0.6, 0.6, 0.6, 1)
}

Window.clearcolor = (0.05, 0.07, 0.10, 1)
Window.softinput_mode = 'below_target'

def get_safe_image(filename):
    if filename and os.path.exists(filename):
        return filename
    return ''

class ForceActiveTextInput(TextInput):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.focus = False
            self.focus = True
            if platform == 'android':
                try:
                    from jnius import autoclass
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    activity = PythonActivity.mActivity
                    Context = autoclass('android.content.Context')
                    imm = activity.getSystemService(Context.INPUT_METHOD_SERVICE)
                    imm.showSoftInput(activity.getCurrentFocus(), 0)
                except Exception:
                    pass
        return super().on_touch_down(touch)

class RoundedCard(BoxLayout):
    def __init__(self, bg_color=None, radius=16, **kwargs):
        super().__init__(**kwargs)
        self.custom_bg = bg_color
        self.radius = radius
        with self.canvas.before:
            color_val = self.custom_bg if self.custom_bg else THEME["card_bg"]
            Color(*color_val)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(self.radius)])
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

class CardButton(ButtonBehavior, BoxLayout):
    pass

class BackHandlingScreen(Screen):
    def on_enter(self):
        Window.bind(on_keyboard=self._handle_back_key)

    def on_leave(self):
        Window.unbind(on_keyboard=self._handle_back_key)

    def _handle_back_key(self, window, key, *args):
        if key == 27:
            if self.manager.current != 'dashboard':
                self.manager.current = 'dashboard'
                return True
        return False

class DashboardScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        self.root_layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(14), size_hint_y=None)
        self.root_layout.bind(minimum_height=self.root_layout.setter('height'))

        header_card = RoundedCard(bg_color=THEME["header_bg"], radius=16, orientation="horizontal", padding=dp(12), spacing=dp(12), size_hint_y=None, height=dp(85))
        
        logo_path = get_safe_image('app_logo.png')
        if not logo_path:
            logo_path = get_safe_image('app_icon.png')
            
        logo_img = Image(source=logo_path, size_hint=(None, None), size=(dp(65), dp(65)), allow_stretch=True, keep_ratio=True)
        header_card.add_widget(logo_img)
        
        title_box = BoxLayout(orientation="vertical", spacing=dp(3))
        app_title = Label(text="KaamKit", font_size='22sp', bold=True, color=THEME["highlight"], halign="left", valign="middle")
        app_title.bind(size=app_title.setter('text_size'))
        app_sub = Label(text="Smart & Fast Tools", font_size='13sp', color=THEME["sub_text"], halign="left", valign="middle")
        app_sub.bind(size=app_sub.setter('text_size'))
        title_box.add_widget(app_title)
        title_box.add_widget(app_sub)
        header_card.add_widget(title_box)
        
        self.root_layout.add_widget(header_card)

        ad_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=dp(8), size_hint_y=None, height=dp(55))
        ad_label = Label(text="📢 [ Banner Ad Space / Google AdMob ]", font_size='12sp', color=THEME["warn"], bold=True, halign='center', valign='middle')
        ad_label.bind(size=ad_label.setter('text_size'))
        ad_card.add_widget(ad_label)
        self.root_layout.add_widget(ad_card)

        quick_bar = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(6), spacing=dp(4), size_hint_y=None, height=dp(65))
        quick_bar.add_widget(Label(text="Quick Tools", font_size='11sp', color=THEME["warn"], bold=True))
        q_btns_layout = BoxLayout(orientation="horizontal", spacing=dp(5))
        for t_name, t_screen in [("Weight", "weight"), ("Calculator", "normal_calc"), ("GST", "gst"), ("Discount", "discount")]:
            qb = Button(text=t_name, font_size='11sp', bold=True, background_color=THEME["btn_bg"], color=(1,1,1,1))
            qb.bind(on_press=lambda x, s=t_screen: setattr(self.manager, 'current', s))
            q_btns_layout.add_widget(qb)
        quick_bar.add_widget(q_btns_layout)
        self.root_layout.add_widget(quick_bar)

        all_buttons_data = [
            ("Weight ↔ Price", "weight", "weight_price_calculator.png"),
            ("GST Calculator", "gst", "gst_calculator.png"),
            ("Calculator", "normal_calc", "calculator.png"),
            ("Electricity Bill", "electricity", "electricity_bill_calculator.png"),
            ("Discount Calculator", "discount", "discount_calculator.png"),
            ("EMI Calculator", "emi", "emi_calculator.png"),
            ("Profit / Loss", "profit_loss", "profit_loss_calculator.png"),
            ("Percentage", "percentage", "percentage_calculator.png"),
            ("Number to Words", "number_to_word", "number_to_word.png"),
            ("Loan Calculator (Byaj)", "loan", "loan_calculator_icon.png"),
            ("Unit Converter", "converter", "unit_converter.png"),
            ("Age Calculator", "age", "age_calculator.png"),
            ("Fuel Cost Calculator", "fuel", "fuelcost_calculator.png"),
            ("Gold / Metal Rate Calc", "gold_calc", "gold_rate_icon.png"),
            ("Scientific Calculator", "scientific", "scientific_calculator.png"),
            ("Down Payment Calculator", "down_payment", "down_pay_icon.png")
        ]

        grid_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))
        
        for title, name, icon_filename in all_buttons_data:
            card_box = CardButton(orientation="horizontal", padding=dp(4), spacing=dp(6), size_hint_y=None, height=dp(62))
            with card_box.canvas.before:
                Color(*THEME["card_bg"])
                card_box.rect = RoundedRectangle(size=card_box.size, pos=card_box.pos, radius=[dp(10)])
            card_box.bind(size=lambda inst, val: setattr(inst.rect, 'size', val),
                          pos=lambda inst, val: setattr(inst.rect, 'pos', val))
            
            icon_box = BoxLayout(size_hint_x=None, width=dp(50))
            valid_icon = get_safe_image(icon_filename)
            icon_img = Image(source=valid_icon, size_hint=(None, None), size=(dp(48), dp(48)), allow_stretch=True, keep_ratio=True)
            icon_box.add_widget(icon_img)
            
            title_lbl = Label(text=title, font_size='13sp', bold=True, color=THEME["text"], halign='left', valign='middle', size_hint_x=0.70)
            title_lbl.bind(size=title_lbl.setter('text_size'))
            
            fav_btn = Button(text="⭐", font_size='10sp', background_color=(0,0,0,0), size_hint_x=0.15)
            
            card_box.add_widget(icon_box)
            card_box.add_widget(title_lbl)
            card_box.add_widget(fav_btn)
            card_box.bind(on_press=lambda x, n=name: setattr(self.manager, 'current', n))
            
            grid_layout.add_widget(card_box)

        self.root_layout.add_widget(grid_layout)
        scroll.add_widget(self.root_layout)
        self.add_widget(scroll)

# 1. Weight Calculator
class WeightCalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(14), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Weight ↔ Price Calculator", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        rate_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(5)], spacing=dp(5), size_hint_y=None, height=dp(70))
        rate_card.add_widget(Label(text="  KITNA RUPAYE KILO HAI ", font_size='13sp', bold=True, color=THEME["text"], halign='center'))
        self.rate = ForceActiveTextInput(text="300", multiline=False, input_type='number', input_filter="float", font_size='16sp', size_hint_y=None, height=dp(35), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.rate.bind(text=self.calculate_live)
        rate_card.add_widget(self.rate)
        root.add_widget(rate_card)
        
        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(190))
        
        left_col = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=dp(8), spacing=dp(5))
        left_col.add_widget(Label(text=" KITNA SAMAN CHAHIE", font_size='11sp', color=THEME["highlight"], bold=True))
        
        gram_box = BoxLayout(orientation="horizontal", spacing=dp(5), size_hint_y=None, height=dp(32))
        self.gram = ForceActiveTextInput(text="600", multiline=False, input_type='number', input_filter="float", font_size='14sp', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.gram.bind(text=self.calculate_live)
        gram_box.add_widget(self.gram)
        gram_box.add_widget(Label(text="grm", font_size='12sp', color=THEME["sub_text"], size_hint_x=0.35))
        left_col.add_widget(gram_box)
        
        kilo_box = BoxLayout(orientation="horizontal", spacing=dp(5), size_hint_y=None, height=dp(32))
        self.kg = ForceActiveTextInput(text="1", multiline=False, input_type='number', input_filter="float", font_size='14sp', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.kg.bind(text=self.calculate_live)
        kilo_box.add_widget(self.kg)
        kilo_box.add_widget(Label(text="Kg", font_size='12sp', color=THEME["sub_text"], size_hint_x=0.35))
        left_col.add_widget(kilo_box)
        
        left_jawab_card = RoundedCard(bg_color=THEME["header_bg"], radius=8, orientation="vertical", padding=dp(5), size_hint_y=None, height=dp(55))
        left_jawab_card.add_widget(Label(text="RESULT", font_size='10sp', color=THEME["warn"], bold=True))
        self.left_result = Label(text="Total ₹480.00", font_size='13sp', color=THEME["highlight"], bold=True)
        left_jawab_card.add_widget(self.left_result)
        left_col.add_widget(left_jawab_card)
        grid.add_widget(left_col)
        
        right_col = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=dp(8), spacing=dp(5))
        right_col.add_widget(Label(text=" KITNA RUPAYE KA CHAHIE", font_size='11sp', color=THEME["result"], bold=True))
        
        amount_box = BoxLayout(orientation="horizontal", spacing=dp(5), size_hint_y=None, height=dp(32))
        amount_box.add_widget(Label(text="Amt", font_size='12sp', color=THEME["sub_text"], size_hint_x=0.35))
        self.amount = ForceActiveTextInput(text="70", multiline=False, input_type='number', input_filter="float", font_size='14sp', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.amount.bind(text=self.calculate_live)
        amount_box.add_widget(self.amount)
        right_col.add_widget(amount_box)
        right_col.add_widget(BoxLayout(size_hint_y=None, height=dp(32)))
        
        right_jawab_card = RoundedCard(bg_color=THEME["header_bg"], radius=8, orientation="vertical", padding=dp(5), size_hint_y=None, height=dp(55))
        right_jawab_card.add_widget(Label(text="RESULT", font_size='10sp', color=THEME["warn"], bold=True))
        self.right_result = Label(text="Wajan 233 Grm", font_size='12sp', color=THEME["result"], bold=True)
        right_jawab_card.add_widget(self.right_result)
        right_col.add_widget(right_jawab_card)
        grid.add_widget(right_col)
        
        root.add_widget(grid)
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate_live(None, None)

    def calculate_live(self, instance, value):
        try:
            rate = float((self.rate.text or "0").replace(",", ""))
            kg = float(self.kg.text or "0")
            gram = float(self.gram.text or "0")
            total = (kg * rate) + ((gram / 1000) * rate)
            self.left_result.text = f"Total ₹{total:,.2f}"
            amount = float((self.amount.text or "0").replace(",", ""))
            if rate > 0:
                total_gram = (amount / rate) * 1000
                kg2 = int(total_gram // 1000)
                gram2 = int(total_gram % 1000)
                self.right_result.text = f"Wajan {kg2:,} Kg {gram2} Grm" if kg2 > 0 else f"Wajan {gram2} Grm"
            else:
                self.right_result.text = "Wajan: Invalid"
        except Exception:
            self.left_result.text = "Total: Invalid"
            self.right_result.text = "Wajan: Invalid"

# 2. GST Calculator
class GSTCalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(14), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="GST Calculator", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        p_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(5)], spacing=dp(5), size_hint_y=None, height=dp(70))
        p_card.add_widget(Label(text="Original Price (₹)", font_size='13sp', bold=True, color=THEME["text"], halign='center'))
        self.price = ForceActiveTextInput(text="1000", multiline=False, input_type='number', input_filter="float", font_size='16sp', size_hint_y=None, height=dp(35), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.price.bind(text=self.calculate)
        p_card.add_widget(self.price)
        root.add_widget(p_card)
        
        g_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(5)], spacing=dp(5), size_hint_y=None, height=dp(70))
        g_card.add_widget(Label(text="GST Rate (%)", font_size='13sp', bold=True, color=THEME["text"], halign='center'))
        self.gst = ForceActiveTextInput(text="18", multiline=False, input_type='number', input_filter="float", font_size='16sp', size_hint_y=None, height=dp(35), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.gst.bind(text=self.calculate)
        g_card.add_widget(self.gst)
        root.add_widget(g_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(12), spacing=dp(5), size_hint_y=None, height=dp(95))
        res_card.add_widget(Label(text="RESULT", font_size='11sp', color=THEME["warn"], bold=True))
        self.result = Label(text="GST = ₹180.00\nTotal = ₹1,180.00", font_size='15sp', color=THEME["result"], bold=True)
        res_card.add_widget(self.result)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            p = float(self.price.text or 0)
            g = float(self.gst.text or 0)
            amount = p * g / 100
            total = p + amount
            self.result.text = f"GST = ₹{amount:,.2f}\nTotal = ₹{total:,.2f}"
        except:
            self.result.text = "Please enter valid values"

class CircularButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bind(size=self.update_canvas, pos=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            r = min(self.size) * 0.40
            RoundedRectangle(size=self.size, pos=self.pos, radius=[r])

class NormalCalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.apply_theme_colors()

        self.root_box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        with self.root_box.canvas.before:
            self.bg_color_instruction = Color(*self.bg_col)
            self.bg_rect = RoundedRectangle(size=Window.size, pos=(0, 0))
        self.root_box.bind(size=self.update_bg, pos=self.update_bg)

        self.root_box.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))

        self.display_card = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(150), padding=dp(15), spacing=dp(5))
        
        with self.display_card.canvas.before:
            self.card_bg_color = Color(*self.card_bg_col)
            self.card_rect = RoundedRectangle(size=self.display_card.size, pos=self.display_card.pos, radius=[dp(20)])
        self.display_card.bind(size=self.update_card_bg, pos=self.update_card_bg)

        self.expr_lbl = Label(
            text="0", 
            font_size='38sp', 
            bold=True,
            halign='right', 
            valign='middle', 
            color=self.expr_text_col, 
            size_hint_x=None,
            height=dp(50)
        )
        self.expr_lbl.bind(texture_size=self.update_text_width)

        self.expr_scroll = ScrollView(
            size_hint=(1, None), 
            height=dp(55), 
            do_scroll_y=False, 
            do_scroll_x=True,
            bar_width=0
        )
        self.expr_scroll.add_widget(self.expr_lbl)
        self.display_card.add_widget(self.expr_scroll)
        
        self.result_lbl = Label(
            text="0", 
            font_size='20sp', 
            halign='right', 
            valign='middle', 
            color=self.result_text_col, 
            text_size=(Window.width - dp(70), None)
        )
        self.result_lbl.bind(size=self.result_lbl.setter('text_size'))
        
        self.display_card.add_widget(self.result_lbl)
        self.root_box.add_widget(self.display_card)

        self.root_box.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))

        self.grid = GridLayout(cols=4, spacing=dp(10), size_hint=(1, 1), padding=[dp(5), dp(0), dp(5), dp(5)])
        self.rebuild_buttons()
        self.root_box.add_widget(self.grid)

        self.add_widget(self.root_box)

    def apply_theme_colors(self):
        is_dark = THEME.get("is_dark", False)
        if is_dark:
            self.bg_col = (0.05, 0.07, 0.10, 1)
            self.card_bg_col = (0.09, 0.12, 0.17, 1)
            self.expr_text_col = (1.0, 1.0, 1.0, 1)
            self.result_text_col = (0.6, 0.65, 0.75, 1)
            self.btn_num_bg = (0.12, 0.16, 0.22, 1)
            self.btn_num_fg = (0.9, 0.9, 0.9, 1)
            self.btn_op_bg = (0.22, 0.18, 0.15, 1)
            self.btn_op_fg = (1.0, 0.6, 0.4, 1)
            self.btn_eq_bg = (0.98, 0.45, 0.08, 1)
            self.btn_eq_fg = (1, 1, 1, 1)
        else:
            self.bg_col = (0.96, 0.96, 0.98, 1)
            self.card_bg_col = (1.0, 1.0, 1.0, 1)
            self.expr_text_col = (0.1, 0.1, 0.1, 1)
            self.result_text_col = (0.5, 0.5, 0.5, 1)
            self.btn_num_bg = (1.0, 1.0, 1.0, 1)
            self.btn_num_fg = (0.1, 0.1, 0.1, 1)
            self.btn_op_bg = (1.0, 0.94, 0.90, 1)
            self.btn_op_fg = (0.98, 0.45, 0.08, 1)
            self.btn_eq_bg = (0.98, 0.45, 0.08, 1)
            self.btn_eq_fg = (1, 1, 1, 1)

    def rebuild_buttons(self):
        self.grid.clear_widgets()
        buttons = [
            ['AC', '%', 'DEL', '÷'], 
            ['7', '8', '9', '×'], 
            ['4', '5', '6', '-'], 
            ['1', '2', '3', '+'], 
            ['00', '0', '.', '=']
        ]
        
        for row in buttons:
            for label in row:
                if label in ['AC', '%', 'DEL', '÷', '×', '-', '+']:
                    btn_bg = self.btn_op_bg
                    btn_fg = self.btn_op_fg
                elif label == '=':
                    btn_bg = self.btn_eq_bg
                    btn_fg = self.btn_eq_fg
                else:
                    btn_bg = self.btn_num_bg
                    btn_fg = self.btn_num_fg
                
                font_sz = '24sp' if label in ['AC', 'DEL', '%'] else '26sp'
                btn = CircularButton(text=label, font_size=font_sz, bold=True, color=btn_fg)
                btn.bg_color = btn_bg
                btn.bind(on_press=self.on_button_press)
                self.grid.add_widget(btn)

    def update_theme(self):
        self.apply_theme_colors()
        self.bg_color_instruction.rgba = self.bg_col
        self.card_bg_color.rgba = self.card_bg_col
        self.expr_lbl.color = self.expr_text_col
        self.result_lbl.color = self.result_text_col
        self.rebuild_buttons()

    def on_enter(self):
        super().on_enter()
        self.update_theme()

    def update_card_bg(self, instance, value):
        self.card_rect.size = instance.size
        self.card_rect.pos = instance.pos

    def update_text_width(self, *args):
        self.expr_lbl.width = max(self.expr_lbl.texture_size[0], self.expr_scroll.width)
        self.expr_scroll.scroll_x = 1.0

    def update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def format_with_commas(self, number_str):
        try:
            number_str = str(number_str).replace(',', '')
            if '.' in number_str:
                parts = number_str.split('.')
                integer_part = int(parts[0]) if parts[0] else 0
                decimal_part = parts[1]
                formatted_int = f"{integer_part:,}"
                return f"{formatted_int}.{decimal_part}"
            else:
                return f"{int(number_str):,}"
        except:
            return str(number_str)

    def format_expression_with_commas(self, expr_str):
        if not expr_str:
            return "0"
        tokens = re.split(r'([\+\-\*/×÷%])', expr_str)
        formatted_tokens = []
        for token in tokens:
            if token in ['+', '-', '*', '/', '×', '÷', '%'] or not token:
                formatted_tokens.append(token)
            else:
                clean_token = token.replace(',', '')
                if clean_token:
                    formatted_tokens.append(self.format_with_commas(clean_token))
                else:
                    formatted_tokens.append(token)
        return "".join(formatted_tokens)

    def on_button_press(self, instance):
        txt = instance.text
        raw_display = self.expr_lbl.text
        current = raw_display.replace(',', '')

        if current == "0" or current == "Error":
            current = ""

        if txt == 'AC':
            self.expr_lbl.text = "0"
            self.result_lbl.text = "0"
        elif txt == 'DEL':
            new_val = current[:-1] if len(current) > 1 else "0"
            self.expr_lbl.text = self.format_expression_with_commas(new_val)
            self.update_live_result(self.expr_lbl.text)
        elif txt == '=':
            try:
                res = self.evaluate_expression(raw_display)
                res_str = str(res)
                formatted_res = self.format_with_commas(res_str)
                self.expr_lbl.text = formatted_res
                self.result_lbl.text = "= " + formatted_res
            except:
                self.result_lbl.text = "Error"
        elif txt == '%':
            new_val = current + '%'
            self.expr_lbl.text = self.format_expression_with_commas(new_val)
            self.update_live_result(self.expr_lbl.text)
        elif txt in ['+', '-', '×', '÷']:
            if current and current[-1] in ['+', '-', '×', '÷']:
                current = current[:-1]
            new_val = current + txt
            self.expr_lbl.text = self.format_expression_with_commas(new_val)
        else:
            new_val = current + txt
            self.expr_lbl.text = self.format_expression_with_commas(new_val)
            self.update_live_result(self.expr_lbl.text)

    def evaluate_expression(self, expr_str):
        clean_expr = str(expr_str).replace('×', '*').replace('÷', '/').replace(',', '')
        if not clean_expr:
            return 0
        
        match = re.search(r'([\d\.]+)\s*([\+\-\*/])\s*([\d\.]+)%', clean_expr)
        if match:
            base = float(match.group(1))
            op = match.group(2)
            pct = float(match.group(3))
            
            if op == '+':
                return base + (base * pct / 100.0)
            elif op == '-':
                return base - (base * pct / 100.0)
            elif op == '*':
                return base * (pct / 100.0)
            elif op == '/':
                return (base / (pct / 100.0)) if pct != 0 else 0

        if '%' in clean_expr:
            clean_expr = clean_expr.replace('%', '/100')
            
        return eval(clean_expr, {"__builtins__": None}, {})

    def update_live_result(self, expr_str):
        try:
            clean_expr = str(expr_str).replace('×', '*').replace('÷', '/').replace(',', '')
            if clean_expr and clean_expr[-1] in ['+', '-', '*', '/']:
                clean_expr = clean_expr[:-1]
            if clean_expr:
                res = self.evaluate_expression(clean_expr)
                self.result_lbl.text = "= " + self.format_with_commas(str(res))
            else:
                self.result_lbl.text = "0"
        except:
            pass

# 4. Electricity Bill Calculator
class ElectricityBillScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Electricity Bill Calculator", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        u_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        u_card.add_widget(Label(text="Enter Units Consumed", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.units = ForceActiveTextInput(text="150", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.units.bind(text=self.calculate)
        u_card.add_widget(self.units)
        root.add_widget(u_card)
        
        r_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        r_card.add_widget(Label(text="Rate per Unit (₹)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.rate = ForceActiveTextInput(text="7", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.rate.bind(text=self.calculate)
        r_card.add_widget(self.rate)
        root.add_widget(r_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), spacing=dp(4), size_hint_y=None, height=dp(85))
        res_card.add_widget(Label(text="RESULT", font_size='11sp', color=THEME["warn"], bold=True))
        self.result = Label(text="Total Bill = ₹1,050.00", font_size='14sp', color=THEME["result"], bold=True)
        res_card.add_widget(self.result)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            u = float(self.units.text or 0)
            r = float(self.rate.text or 0)
            total = u * r
            self.result.text = f"Total Bill = ₹{total:,.2f}"
        except:
            self.result.text = "Please enter valid values"

# 5. Discount Calculator
class DiscountCalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Discount Calculator", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        p_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        p_card.add_widget(Label(text="Original Price (₹)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.price = ForceActiveTextInput(text="2000", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.price.bind(text=self.calculate)
        p_card.add_widget(self.price)
        root.add_widget(p_card)
        
        d_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        d_card.add_widget(Label(text="Discount (%)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.discount = ForceActiveTextInput(text="20", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.discount.bind(text=self.calculate)
        d_card.add_widget(self.discount)
        root.add_widget(d_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), spacing=dp(4), size_hint_y=None, height=dp(85))
        res_card.add_widget(Label(text="RESULT", font_size='11sp', color=THEME["warn"], bold=True))
        self.result = Label(text="You Save = ₹400.00\nFinal Price = ₹1,600.00", font_size='14sp', color=THEME["result"], bold=True)
        res_card.add_widget(self.result)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            p = float(self.price.text or 0)
            d = float(self.discount.text or 0)
            save = p * d / 100
            final = p - save
            self.result.text = f"You Save = ₹{save:,.2f}\nFinal Price = ₹{final:,.2f}"
        except:
            self.result.text = "Please enter valid values"

# 6. EMI Calculator
class EMICalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="EMI Calculator", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        p_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        p_card.add_widget(Label(text="Loan Amount (₹)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.principal = ForceActiveTextInput(text="500000", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.principal.bind(text=self.calculate)
        p_card.add_widget(self.principal)
        root.add_widget(p_card)
        
        r_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        r_card.add_widget(Label(text="Interest Rate % (Per Annum)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.rate = ForceActiveTextInput(text="10", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.rate.bind(text=self.calculate)
        r_card.add_widget(self.rate)
        root.add_widget(r_card)
        
        t_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        t_card.add_widget(Label(text="Tenure (in Months)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.tenure = ForceActiveTextInput(text="12", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.tenure.bind(text=self.calculate)
        t_card.add_widget(self.tenure)
        root.add_widget(t_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), spacing=dp(4), size_hint_y=None, height=dp(95))
        res_card.add_widget(Label(text="RESULT", font_size='11sp', color=THEME["warn"], bold=True))
        self.result = Label(text="Monthly EMI = ₹43,958.33\nTotal Payment = ₹527,500.00", font_size='14sp', color=THEME["result"], bold=True)
        res_card.add_widget(self.result)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            p = float(self.principal.text or 0)
            annual_rate = float(self.rate.text or 0)
            months = float(self.tenure.text or 0)
            if months <= 0:
                self.result.text = "Tenure must be > 0"
                return
            r = annual_rate / (12 * 100)
            if r == 0:
                emi = p / months
            else:
                emi = (p * r * ((1 + r)**months)) / (((1 + r)**months) - 1)
            total_payment = emi * months
            self.result.text = f"Monthly EMI = ₹{emi:,.2f}\nTotal Payment = ₹{total_payment:,.2f}"
        except:
            self.result.text = "Please enter valid values"

# 7. Profit / Loss Calculator
class ProfitLossCalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(14), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Profit / Loss Calculator", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        cp_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(5)], spacing=dp(5), size_hint_y=None, height=dp(70))
        cp_card.add_widget(Label(text="Cost Price / Lagat (₹)", font_size='13sp', bold=True, color=THEME["text"], halign='center'))
        self.cp_input = ForceActiveTextInput(text="500", multiline=False, input_type='number', input_filter="float", font_size='16sp', size_hint_y=None, height=dp(35), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.cp_input.bind(text=self.calculate)
        cp_card.add_widget(self.cp_input)
        root.add_widget(cp_card)
        
        sp_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(5)], spacing=dp(5), size_hint_y=None, height=dp(70))
        sp_card.add_widget(Label(text="Selling Price / Bikri (₹)", font_size='13sp', bold=True, color=THEME["text"], halign='center'))
        self.sp_input = ForceActiveTextInput(text="650", multiline=False, input_type='number', input_filter="float", font_size='16sp', size_hint_y=None, height=dp(35), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.sp_input.bind(text=self.calculate)
        sp_card.add_widget(self.sp_input)
        root.add_widget(sp_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(12), spacing=dp(6), size_hint_y=None, height=dp(100))
        res_card.add_widget(Label(text="RESULT", font_size='11sp', color=THEME["warn"], bold=True))
        self.result_lbl = Label(text="Profit: ₹150.00 (30.00% Munafa)", font_size='14sp', color=THEME["result"], bold=True)
        res_card.add_widget(self.result_lbl)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            cp = float(self.cp_input.text or 0)
            sp = float(self.sp_input.text or 0)
            if cp <= 0:
                self.result_lbl.text = "Enter valid Cost Price"
                return
            diff = sp - cp
            percent = (abs(diff) / cp) * 100
            if diff > 0:
                self.result_lbl.text = f"Profit: ₹{diff:,.2f} ({percent:.2f}% Munafa)"
            elif diff < 0:
                self.result_lbl.text = f"Loss: ₹{abs(diff):,.2f} ({percent:.2f}% Nuksan)"
            else:
                self.result_lbl.text = "No Profit, No Loss"
        except Exception:
            self.result_lbl.text = "Invalid Input Values"

# 8. Percentage Calculator
class PercentageCalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(14), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Percentage Calculator", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        n_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(5)], spacing=dp(5), size_hint_y=None, height=dp(70))
        n_card.add_widget(Label(text="Enter Number", font_size='13sp', bold=True, color=THEME["text"], halign='center'))
        self.number = ForceActiveTextInput(text="800", multiline=False, input_type='number', input_filter="float", font_size='16sp', size_hint_y=None, height=dp(35), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.number.bind(text=self.calculate)
        n_card.add_widget(self.number)
        root.add_widget(n_card)
        
        p_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(5)], spacing=dp(5), size_hint_y=None, height=dp(70))
        p_card.add_widget(Label(text="Percentage (%)", font_size='13sp', bold=True, color=THEME["text"], halign='center'))
        self.percent = ForceActiveTextInput(text="15", multiline=False, input_type='number', input_filter="float", font_size='16sp', size_hint_y=None, height=dp(35), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.percent.bind(text=self.calculate)
        p_card.add_widget(self.percent)
        root.add_widget(p_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(12), spacing=dp(5), size_hint_y=None, height=dp(80))
        res_card.add_widget(Label(text="RESULT", font_size='11sp', color=THEME["warn"], bold=True))
        self.result = Label(text="Result = 120.0", font_size='15sp', color=THEME["result"], bold=True)
        res_card.add_widget(self.result)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            num = float(self.number.text or 0)
            per = float(self.percent.text or 0)
            res = num * per / 100
            self.result.text = f"{per}% of {num} = {res:,.2f}"
        except:
            self.result.text = "Please enter valid values"

# 9. Number to Words / Currency Converter
def english_words(n):
    if n == 0:
        return "Zero"
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
            "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def helper(num):
        if num == 0:
            return ""
        elif num < 20:
            return ones[num] + " "
        elif num < 100:
            return tens[num // 10] + " " + helper(num % 10)
        elif num < 1000:
            return ones[num // 100] + " Hundred " + helper(num % 100)
        elif num < 100000:
            return helper(num // 1000) + "Thousand " + helper(num % 1000)
        elif num < 10000000:
            return helper(num // 100000) + "Lakh " + helper(num % 100000)
        else:
            return helper(num // 10000000) + "Crore " + helper(num % 10000000)

    return helper(n).strip()

class NumberToWordScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Number to Words / Converter", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)

        n_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        n_card.add_widget(Label(text="Enter Number / Amount", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.number_input = ForceActiveTextInput(text="5000", multiline=False, input_type='number', input_filter="int", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.number_input.bind(text=self.calculate)
        n_card.add_widget(self.number_input)
        root.add_widget(n_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(12), spacing=dp(6), size_hint_y=None, height=dp(110))
        res_card.add_widget(Label(text="RESULT IN WORDS", font_size='11sp', color=THEME["warn"], bold=True))
        self.result = Label(text="", font_size='14sp', color=THEME["result"], bold=True, halign='center', text_size=(Window.width - dp(60), None))
        self.result.bind(size=self.result.setter('text_size'))
        res_card.add_widget(self.result)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            val = int(self.number_input.text or 0)
            words = english_words(val)
            self.result.text = f"{words} Rupees"
        except:
            self.result.text = "Please enter a valid number"

# 10. Loan Calculator (Byaj)
class LoanCalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Loan Calculator (Byaj)", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        p_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        p_card.add_widget(Label(text="Principal Amount (₹)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.principal = ForceActiveTextInput(text="50000", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.principal.bind(text=self.calculate)
        p_card.add_widget(self.principal)
        root.add_widget(p_card)
        
        r_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        r_card.add_widget(Label(text="Interest Rate % (Per Month)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.rate = ForceActiveTextInput(text="2", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.rate.bind(text=self.calculate)
        r_card.add_widget(self.rate)
        root.add_widget(r_card)
        
        t_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        t_card.add_widget(Label(text="Time (in Months)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.time = ForceActiveTextInput(text="6", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.time.bind(text=self.calculate)
        t_card.add_widget(self.time)
        root.add_widget(t_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), spacing=dp(4), size_hint_y=None, height=dp(85))
        res_card.add_widget(Label(text="RESULT", font_size='11sp', color=THEME["warn"], bold=True))
        self.result = Label(text="Interest = ₹6,000.00\nTotal = ₹56,000.00", font_size='14sp', color=THEME["result"], bold=True)
        res_card.add_widget(self.result)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            p = float(self.principal.text or 0)
            r = float(self.rate.text or 0)
            t = float(self.time.text or 0)
            interest = (p * r * t) / 100
            total = p + interest
            self.result.text = f"Interest = ₹{interest:,.2f}\nTotal = ₹{total:,.2f}"
        except:
            self.result.text = "Please enter valid values"

# 11. Unit Converter
class UnitConverterScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Unit Converter", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        v_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(5)], spacing=dp(5), size_hint_y=None, height=dp(70))
        v_card.add_widget(Label(text="Enter Value (Kg / Meter)", font_size='13sp', bold=True, color=THEME["text"], halign='center'))
        self.value = ForceActiveTextInput(text="2", multiline=False, input_type='number', input_filter="float", font_size='16sp', size_hint_y=None, height=dp(35), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.value.bind(text=self.calculate)
        v_card.add_widget(self.value)
        root.add_widget(v_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(12), spacing=dp(6), size_hint_y=None, height=dp(110))
        res_card.add_widget(Label(text="RESULT", font_size='12sp', color=THEME["warn"], bold=True))
        self.result = Label(text="Kg to Gram = 2,000 Gram\nMeter to Feet = 6.56 Feet", font_size='15sp', color=THEME["result"], bold=True)
        res_card.add_widget(self.result)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            val = float(self.value.text or 0)
            gram = val * 1000
            feet = val * 3.28084
            self.result.text = f"Kg to Gram = {gram:,.0f} Gram\nMeter to Feet = {feet:,.2f} Feet"
        except:
            self.result.text = "Please enter valid value"

# 12. Age Calculator
class AgeCalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Age Calculator", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        y_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        y_card.add_widget(Label(text="Birth Year (e.g. 2000)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.year_input = ForceActiveTextInput(text="2000", multiline=False, input_type='number', input_filter="int", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.year_input.bind(text=self.calculate)
        y_card.add_widget(self.year_input)
        root.add_widget(y_card)
        
        m_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        m_card.add_widget(Label(text="Birth Month (1-12)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.month_input = ForceActiveTextInput(text="1", multiline=False, input_type='number', input_filter="int", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.month_input.bind(text=self.calculate)
        m_card.add_widget(self.month_input)
        root.add_widget(m_card)
        
        d_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        d_card.add_widget(Label(text="Birth Day (1-31)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.day_input = ForceActiveTextInput(text="1", multiline=False, input_type='number', input_filter="int", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.day_input.bind(text=self.calculate)
        d_card.add_widget(self.day_input)
        root.add_widget(d_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), spacing=dp(4), size_hint_y=None, height=dp(80))
        res_card.add_widget(Label(text="RESULT", font_size='11sp', color=THEME["warn"], bold=True))
        self.result = Label(text="Your Age here", font_size='15sp', color=THEME["result"], bold=True)
        res_card.add_widget(self.result)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            y = int(self.year_input.text or 2000)
            m = int(self.month_input.text or 1)
            d = int(self.day_input.text or 1)
            birth_date = datetime.date(y, m, d)
            today = datetime.date.today()
            if birth_date > today:
                self.result.text = "Future date not allowed!"
                return
            age_years = today.year - birth_date.year
            age_months = today.month - birth_date.month
            age_days = today.day - birth_date.day
            if age_days < 0:
                age_months -= 1
                age_days += 30
            if age_months < 0:
                age_years -= 1
                age_months += 12
            self.result.text = f"{age_years} Years, {age_months} Months, {age_days} Days"
        except:
            self.result.text = "Please enter correct date"

# 13. Fuel Cost Calculator
class FuelCostCalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Fuel Cost Calculator", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        d_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        d_card.add_widget(Label(text="Total Distance (in Km)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.distance = ForceActiveTextInput(text="150", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.distance.bind(text=self.calculate)
        d_card.add_widget(self.distance)
        root.add_widget(d_card)
        
        m_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        m_card.add_widget(Label(text="Mileage (Km per Litre)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.mileage = ForceActiveTextInput(text="40", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.mileage.bind(text=self.calculate)
        m_card.add_widget(self.mileage)
        root.add_widget(m_card)
        
        p_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        p_card.add_widget(Label(text="Fuel Price per Litre (₹)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.price = ForceActiveTextInput(text="100", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.price.bind(text=self.calculate)
        p_card.add_widget(self.price)
        root.add_widget(p_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), spacing=dp(4), size_hint_y=None, height=dp(85))
        res_card.add_widget(Label(text="RESULT", font_size='11sp', color=THEME["warn"], bold=True))
        self.result = Label(text="Fuel Needed = 3.75 Litres\nTotal Cost = ₹375.00", font_size='14sp', color=THEME["result"], bold=True)
        res_card.add_widget(self.result)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            dist = float(self.distance.text or 0)
            mil = float(self.mileage.text or 0)
            prc = float(self.price.text or 0)
            if mil <= 0:
                self.result.text = "Mileage must be > 0"
                return
            litres = dist / mil
            total_cost = litres * prc
            self.result.text = f"Fuel Needed = {litres:.2f} Litres\nTotal Cost = ₹{total_cost:,.2f}"
        except:
            self.result.text = "Please enter valid values"

# 14. Gold / Metal Rate Calculator
class GoldCalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(14), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Gold / Precious Metal Rate Calc", font_size='15sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)

        r_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(5)], spacing=dp(5), size_hint_y=None, height=dp(70))
        r_card.add_widget(Label(text="10 Gram Rate (₹)", font_size='13sp', bold=True, color=THEME["text"], halign='center'))
        self.rate_10g = ForceActiveTextInput(text="72000", multiline=False, input_type='number', input_filter="float", font_size='16sp', size_hint_y=None, height=dp(35), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.rate_10g.bind(text=self.calculate)
        r_card.add_widget(self.rate_10g)
        root.add_widget(r_card)

        g_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(5)], spacing=dp(5), size_hint_y=None, height=dp(70))
        g_card.add_widget(Label(text="Required Weight (Grams e.g. 3.25)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.weight_req = ForceActiveTextInput(text="3.25", multiline=False, input_type='number', input_filter="float", font_size='16sp', size_hint_y=None, height=dp(35), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.weight_req.bind(text=self.calculate)
        g_card.add_widget(self.weight_req)
        root.add_widget(g_card)

        m_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(5)], spacing=dp(5), size_hint_y=None, height=dp(70))
        m_card.add_widget(Label(text="Making Charges / Tax (%)", font_size='13sp', bold=True, color=THEME["text"], halign='center'))
        self.making_chg = ForceActiveTextInput(text="3", multiline=False, input_type='number', input_filter="float", font_size='16sp', size_hint_y=None, height=dp(35), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.making_chg.bind(text=self.calculate)
        m_card.add_widget(self.making_chg)
        root.add_widget(m_card)

        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(12), spacing=dp(6), size_hint_y=None, height=dp(110))
        res_card.add_widget(Label(text="RESULT", font_size='11sp', color=THEME["warn"], bold=True))
        self.result = Label(text="Metal Value = ₹23,400.00\nTotal with Charges = ₹24,102.00", font_size='14sp', color=THEME["result"], bold=True)
        res_card.add_widget(self.result)
        root.add_widget(res_card)

        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            r10 = float(self.rate_10g.text or 0)
            wt = float(self.weight_req.text or 0)
            chg_pct = float(self.making_chg.text or 0)
            rate_per_gram = r10 / 10.0
            base_val = rate_per_gram * wt
            extra_val = base_val * (chg_pct / 100.0)
            total_val = base_val + extra_val
            self.result.text = f"Metal Value = ₹{base_val:,.2f}\nTotal with Charges = ₹{total_val:,.2f}"
        except:
            self.result.text = "Please enter valid values"

# 15. Scientific Calculator
class ScientificCalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Scientific Calculator", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        e_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=dp(8), spacing=dp(4), size_hint_y=None, height=dp(70))
        e_card.add_widget(Label(text="Enter Expression (e.g. 2^3 or sqrt(16))", font_size='11sp', bold=True, color=THEME["text"], halign='center'))
        self.expr = ForceActiveTextInput(text="2^3", multiline=False, font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.expr.bind(text=self.calculate)
        e_card.add_widget(self.expr)
        root.add_widget(e_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), spacing=dp(4), size_hint_y=None, height=dp(85))
        res_card.add_widget(Label(text="RESULT", font_size='11sp', color=THEME["warn"], bold=True))
        self.result = Label(text="Result = 8.0000", font_size='14sp', color=THEME["result"], bold=True)
        res_card.add_widget(self.result)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)

        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            val_str = self.expr.text.strip()
            if not val_str:
                self.result.text = "Result = 0"
                return
            
            val_str = val_str.replace('^', '**')
            
            safe_dict = {
                "sqrt": math.sqrt, 
                "sin": math.sin, 
                "cos": math.cos, 
                "tan": math.tan, 
                "log": math.log10,
                "ln": math.log,
                "pi": math.pi, 
                "e": math.e,
                "abs": abs,
                "pow": pow
            }
            
            res = eval(val_str, {"__builtins__": None}, safe_dict)
            if isinstance(res, (int, float)):
                self.result.text = f"Result = {res:,.4f}"
            else:
                self.result.text = f"Result = {res}"
        except Exception:
            self.result.text = "Invalid Expression"

# 16. Down Payment Calculator Screen
class DownPaymentCalculatorScreen(BackHandlingScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12), size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))
        
        title_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(50))
        title_card.add_widget(Label(text="Down Payment Calculator", font_size='16sp', bold=True, color=THEME["highlight"], halign='center'))
        root.add_widget(title_card)
        
        dp_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        dp_card.add_widget(Label(text="Down Payment (₹)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.down_payment = ForceActiveTextInput(text="20000", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.down_payment.bind(text=self.calculate)
        dp_card.add_widget(self.down_payment)
        root.add_widget(dp_card)
        
        emi_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        emi_card.add_widget(Label(text="Monthly EMI Price (₹)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.monthly_emi = ForceActiveTextInput(text="5000", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.monthly_emi.bind(text=self.calculate)
        emi_card.add_widget(self.monthly_emi)
        root.add_widget(emi_card)
        
        m_card = RoundedCard(bg_color=THEME["card_bg"], radius=12, orientation="vertical", padding=[dp(10), dp(4)], spacing=dp(3), size_hint_y=None, height=dp(65))
        m_card.add_widget(Label(text="Tenure (in Months)", font_size='12sp', bold=True, color=THEME["text"], halign='center'))
        self.months = ForceActiveTextInput(text="24", multiline=False, input_type='number', input_filter="float", font_size='15sp', size_hint_y=None, height=dp(32), halign='center', background_color=THEME["input_bg"], foreground_color=THEME["input_fg"])
        self.months.bind(text=self.calculate)
        m_card.add_widget(self.months)
        root.add_widget(m_card)
        
        res_card = RoundedCard(bg_color=THEME["header_bg"], radius=12, orientation="vertical", padding=dp(10), spacing=dp(4), size_hint_y=None, height=dp(110))
        res_card.add_widget(Label(text="RESULT", font_size='11sp', color=THEME["warn"], bold=True, halign='center'))
        self.result = Label(text="", font_size='14sp', color=THEME["result"], bold=True, halign='center')
        res_card.add_widget(self.result)
        root.add_widget(res_card)
        
        back_btn = Button(text="⬅ Back to Dashboard", font_size='15sp', bold=True, background_color=THEME["back_btn_bg"], color=(1,1,1,1), size_hint_y=None, height=dp(48))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        root.add_widget(back_btn)
        
        scroll.add_widget(root)
        self.add_widget(scroll)
        self.calculate(None, None)

    def calculate(self, instance, value):
        try:
            dp_val = float(self.down_payment.text or 0)
            emi_val = float(self.monthly_emi.text or 0)
            m = float(self.months.text or 0)
            
            if m <= 0:
                self.result.text = "Enter valid months"
                return
                
            total_emi_paid = emi_val * m
            total_kimat = dp_val + total_emi_paid
            
            self.result.text = f"Total EMI Paid = ₹{total_emi_paid:,.2f}\nTotal Kimat = ₹{total_kimat:,.2f}"
        except:
            self.result.text = "Please enter valid values"

class KaamKitApp(App):
    def trigger_vibration(self, window, touch):
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                Context = autoclass('android.content.Context')
                View = autoclass('android.view.View')
                
                # Yeh Android ke haptic feedback / vibration ko trigger karega chahe phone general mode mein ho ya silent mein
                vibe = activity.getSystemService(Context.VIBRATOR_SERVICE)
                if vibe and vibe.hasVibrator():
                    vibe.vibrate(30) # 30 milliseconds ka halka vibration tap par
            except Exception:
                pass

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(WeightCalculatorScreen(name="weight"))
        self.sm.add_widget(GSTCalculatorScreen(name="gst"))
        self.sm.add_widget(NormalCalculatorScreen(name="normal_calc"))
        self.sm.add_widget(ElectricityBillScreen(name="electricity"))
        self.sm.add_widget(DiscountCalculatorScreen(name="discount"))
        self.sm.add_widget(EMICalculatorScreen(name="emi"))
        self.sm.add_widget(ProfitLossCalculatorScreen(name="profit_loss"))
        self.sm.add_widget(PercentageCalculatorScreen(name="percentage"))
        self.sm.add_widget(NumberToWordScreen(name="number_to_word"))
        self.sm.add_widget(LoanCalculatorScreen(name="loan"))
        self.sm.add_widget(UnitConverterScreen(name="converter"))
        self.sm.add_widget(AgeCalculatorScreen(name="age"))
        self.sm.add_widget(FuelCostCalculatorScreen(name="fuel"))
        self.sm.add_widget(GoldCalculatorScreen(name="gold_calc"))
        self.sm.add_widget(ScientificCalculatorScreen(name="scientific"))
        self.sm.add_widget(DownPaymentCalculatorScreen(name="down_payment"))
        
        # Har touch/click par vibration trigger karne ke liye bind kiya hai
        Window.bind(on_touch_down=self.trigger_vibration)
        return self.sm

if __name__ == "__main__":
    KaamKitApp().run()
