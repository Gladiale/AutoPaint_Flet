import flet as ft
import pyautogui
import keyboard
from pynput import mouse
import time

pyautogui.FAILSAFE = True

# 配列でマウスポジションを格納
mouse_position_list = []
color_list = []
processing_list = []
# 偏移量
deviation_data = {
    # i: [value, pages]
}

# 現在のマウス位置取得
def getMousePoint(page: ft.Page, lv: ft.ListView, dlg_modal: ft.AlertDialog):
    x_position, y_position = pyautogui.position()
    if not (x_position, y_position) in mouse_position_list:
        mouse_position_list.append((x_position, y_position))
        processing_list.append(len(mouse_position_list) - 1)
    # print(mouse_position_list)
    # print("append:", processing_list)
    refresh(page, lv, dlg_modal)

# 現在位置のカラーを取得 (https://boook24.com/?p=375)
def getRGBColor(page: ft.Page, lv: ft.ListView, dlg_modal: ft.AlertDialog):
    if len(color_list) < len(mouse_position_list):
        x, y = pyautogui.position()
        RGB = pyautogui.pixel(x, y)
        color_list.append(RGB)
        refresh(page, lv, dlg_modal)

# 自動ペイント
paint_page = 1
try_times = 0
total_times = 5

def autoPaint(page: ft.Page, start_icon: ft.IconButton):
    global try_times
    if int(paint_page) == 1:
        page_number = paint_page
        for i in processing_list:
            if try_times > total_times:
                try_times = 0
                # print("プログラム強制終了_最終loop")
                start_icon.icon = "running_with_errors"
                start_icon.icon_color = "red"
                page.update()
                break
            paintProcess(i, page_number)
    else:
        for page_number in range(int(paint_page)):
            if try_times > total_times:
                try_times = 0
                # print("プログラム強制終了_最終loop")
                start_icon.icon = "running_with_errors"
                start_icon.icon_color = "red"
                page.update()
                break
            for i in processing_list:
                # 無限ループの場合のループを中止
                if try_times > total_times:
                    # print("プログラム強制終了_loop_list")
                    break
                paintProcess(i, page_number)
            pyautogui.press('>')
            pyautogui.press('enter')
            time.sleep(0.5)
    if not start_icon.icon == "running_with_errors":
        start_icon.icon = "published_with_changes"
        page.update()

# 強制終了関数
# def suspend_func(page: ft.Page, start_icon: ft.IconButton, times):
#     if times > total_times:
#         times = 0
#         print("プログラム強制終了_最終loop")
#         start_icon.icon = "running_with_errors"
#         start_icon.icon_color = "red"
#         page.update()
#         return

# 白い場所の座標
white_color_position = (30, 800)
def find_color_border():
    global try_times
    try:
        # color_borderの色を白にする
        pyautogui.mouseDown(white_color_position[0], white_color_position[1], button='right')
        pyautogui.mouseUp(button='right')

        color_border = pyautogui.locateOnScreen('./images/color_border.png', confidence=0.9)
        x, y = pyautogui.center(color_border)
        pyautogui.click(x, y)
    except Exception:
        time.sleep(0.5)
        # 無限ループの場合は強制終了
        if try_times > total_times:
            return
        try_times += 1
        find_color_border()

# 偏差量
offset = 50
def find_RGB_input():
    global try_times
    try:
        RGB_input = pyautogui.locateOnScreen('./images/RGB_input.png', confidence=0.9)
        x, y = pyautogui.center(RGB_input)
        pyautogui.click(x + offset, y)
    except Exception:
        time.sleep(0.5)
        # 無限ループの場合は強制終了
        if try_times > total_times:
            return
        try_times += 1
        find_RGB_input()

def paintProcess(i, page_number):
    global try_times
    try_times = 0

    # 仕上げ開始(注意：英語の入力方式に変えて)
    # pyautogui.press('f')

    find_color_border()
    find_RGB_input()

    # 無限ループの場合は強制終了
    if try_times > total_times:
        return

    pyautogui.hotkey('ctrl', 'a')
    pyautogui.write(str(color_list[i][0]))
    pyautogui.press('tab')
    pyautogui.write(str(color_list[i][1]))
    pyautogui.press('tab')
    pyautogui.write(str(color_list[i][2]))
    pyautogui.press('enter')

    time.sleep(0.3)
    # ここは［フィル］のショットカットキー
    pyautogui.press('f')
    # ページごとに偏移量を付ける
    if i in deviation_data.keys():
        deviation_value = deviation_data[i][0]
        deviation_page = deviation_data[i][1]
        if deviation_page > 0 or not deviation_page == "":
            if page_number <= deviation_page:
                # print(mouse_position_list[i][1] + deviation_value * page_number)
                pyautogui.mouseDown(mouse_position_list[i][0], mouse_position_list[i][1] + deviation_value * page_number)
            else:
                pyautogui.mouseDown(mouse_position_list[i][0], mouse_position_list[i][1])
        else:
            pyautogui.mouseDown(mouse_position_list[i][0], mouse_position_list[i][1])
    else:
        # print("偏移量なし")
        pyautogui.mouseDown(mouse_position_list[i][0], mouse_position_list[i][1])
    pyautogui.mouseUp()


# マウスを特定な座標に移動
def text_container_click(e):
    x = mouse_position_list[e.control.data][0]
    y = mouse_position_list[e.control.data][1]
    pyautogui.moveTo(x, y, 0.3)


# flet画面の更新
def refresh(page: ft.Page, lv: ft.ListView, dlg_modal: ft.AlertDialog):
    # colorの再設定
    def color_container_click(e: ft.ContainerTapEvent):
        e.control.blur=10
        page.update()
        # 特定colorの更新(https://yumarublog.com/python/mouse-keyboard/)
        def colorReset(x, y, button, pressed):
            if button == mouse.Button.middle and not pressed:
                # x, y = pyautogui.position()
                RGB = pyautogui.pixel(x, y)
                color_list[e.control.data] = RGB
                refresh(page, lv, dlg_modal)
                return False
        with mouse.Listener(on_click=colorReset) as listener:
            listener.join()

    # 特定な座標と色を削除
    def delete_item(e):
        index = e.control.data
        mouse_position_list.pop(index)
        if index >= len(color_list):
            pass
        else:
            color_list.pop(index)
        # 注意！(indexを削除した後, indexの後ろの値は全部-1の必要があり)
        # リスト型 processing_list
        if index in processing_list:
            processing_list.remove(index)
            # print("remove:", processing_list)
        for data in processing_list:
            # print(data)
            if index < data:
                processing_list.append(data - 1)
                processing_list.remove(data)
                processing_list.sort()
        # 辞書型 deviation_data
        if index in deviation_data:
            del deviation_data[index]
        key_list = []
        for key in deviation_data.keys():
            # print("key:", key)
            if index < key:
                key_list.append(key)
        key_list.sort()
        if not key_list == []:
            for data in key_list:
                deviation_data[data -1] = deviation_data.pop(data)
        # print("key_list:", key_list)
        # print("for:", processing_list)
        # print("del:", deviation_data)
        refresh(page, lv, dlg_modal)

    # 座標と色を無視
    def un_matching(e):
        data_number = e.control.data
        global processing_list
        if e.control.icon == "check":
            processing_list.remove(data_number)
        else:
            processing_list.append(data_number)
            processing_list.sort()
        # print(processing_list)
        refresh(page, lv, dlg_modal)

    # ダイアログを開ける
    def open_dlg_modal(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        key = e.control.data
        dlg_modal.data = key
        if key in deviation_data:
            # print(vars(dlg_modal.content))
            dlg_modal.content._Row__controls[0].value = deviation_data[key][0]
            dlg_modal.content._Row__controls[1].value = deviation_data[key][1]
        else:
            dlg_modal.content._Row__controls[0].value = ""
            dlg_modal.content._Row__controls[1].value = ""
        page.update()


    # list中のデータ全部消す
    lv.controls.clear()
    for i in range(len(mouse_position_list)):
        # 座標と色を無視の変化
        if i in processing_list:
            icon_name = "check"
            icon_color_process = None
        else:
            icon_name = "clear"
            icon_color_process = "#ff0000"
        # 偏移量の変化
        if i in deviation_data:
            icon_color_modal = "#ff0000"
        else:
            icon_color_modal = None
        if i < len(color_list):
            # RGB配列を16進数表現へ変換(https://code.tiblab.net/python/color_code_transform)
            color = color_list[i]
            html_color = '#%02X%02X%02X' % (color[0],color[1],color[2])
            lv.controls.append(ft.Row([
                ft.IconButton(icon=icon_name, icon_size=20, data=i, icon_color=icon_color_process, on_click=un_matching),
                ft.Container(content=ft.Text(f"座標: {mouse_position_list[i]}"), width=120, data=i, on_click=text_container_click),
                # dataプロパティは自由にデータを格納してOK！(https://rakuraku-engineer.com/posts/flet-base/)
                ft.Container(bgcolor=html_color, width=60, height=20, data=i, ink=True,
                             on_click=color_container_click),
                ft.IconButton(ft.icons.TIPS_AND_UPDATES, icon_size=23, data=i, icon_color=icon_color_modal, on_click=open_dlg_modal),
                ft.IconButton(ft.icons.DELETE_FOREVER_ROUNDED, data=i, on_click=delete_item)
                ],
                alignment=ft.MainAxisAlignment.CENTER
                )
            )
        else:
            lv.controls.append(ft.Row([
                ft.IconButton(icon=icon_name, icon_size=20, data=i, icon_color=icon_color_process, on_click=un_matching),
                ft.Container(content=ft.Text(f"座標: {mouse_position_list[i]}"), width=115, data=i, on_click=text_container_click),
                ft.Container(content=ft.Text("色未指定", text_align="CENTER"), width=60, height=20),
                ft.IconButton(ft.icons.TIPS_AND_UPDATES, icon_size=23, data=i, icon_color=icon_color_modal, on_click=open_dlg_modal),
                ft.IconButton(ft.icons.DELETE_FOREVER_ROUNDED, data=i, on_click=delete_item)
                ],
                alignment=ft.MainAxisAlignment.CENTER
                )
            )
    page.update()

def main(page: ft.Page):
    # https://flet.dev/docs/controls/page/
    page.title = "色塗り自動化"
    page.window_width = 400  # 幅
    page.window_height = 500  # 高さ
    page.window_resizable = False  # ウィンドウサイズ変更可否
    page.window_always_on_top = True  # ウィンドウを最前面に固定
    page.window_center() # ウィンドウをデスクトップの中心に移動
    # page.window_top = 0  # 位置(TOP)
    # page.window_left =1920 / 1.25 - 300  # 位置(LEFT)
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER  # 多分縦方向の中央寄せ
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER  # 多分水平方向の中央寄せ

    # ---------画面サイズ取得---------
    x, y = pyautogui.size()
    screen_size = ft.Text(f"画面サイズ: x {x}px, y {y}px")

    # themeを切り替え
    def theme_changed(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        # print(theme_icon)
        theme_icon.icon = (
            "dark_mode"
            if  theme_icon.icon == "light_mode"
            else "light_mode"
        )
        page.update()
    page.theme_mode = ft.ThemeMode.LIGHT
    theme_icon = ft.IconButton(ft.icons.LIGHT_MODE, on_click=theme_changed)

    # ウィンドウを最前面に固定
    def desk_changed(e):
        desk_icon.icon = (
            "desktop_access_disabled_sharp"
            if desk_icon.icon == "desktop_windows_sharp"
            else "desktop_windows_sharp"
        )
        page.window_always_on_top = (
            True
            if desk_icon.icon == "desktop_windows_sharp"
            else False
        )
        page.update()
    desk_icon = ft.IconButton(ft.icons.DESKTOP_WINDOWS_SHARP, on_click=desk_changed)

    # 自動ペイントスタート
    def start_paint(e):
        start_icon.icon = (
            "adb"
            if start_icon.icon == "auto_mode"
            else "auto_mode"
        )
        start_icon.icon_color = (
            "green"
            if start_icon.icon == "adb"
            else None
        )
        if start_icon.icon == "running_with_errors" or start_icon.icon == "published_with_changes":
            start_icon.icon = "auto_mode"
        page.update()
        if start_icon.icon == "adb":
            autoPaint(page, start_icon)
    # icons.CANCEL_SCHEDULE_SEND
    start_icon = ft.IconButton(ft.icons.AUTO_MODE, on_click=start_paint)

    control_icons = ft.Row([
        theme_icon, desk_icon, start_icon
    ], alignment=ft.MainAxisAlignment.CENTER)

    def textbox_change(e):
        # nonlocal paint_page
        global paint_page
        paint_page = e.control.value
    paint_page_input = ft.TextField(label="仕上げ枚数", width=140, height=50, on_change=textbox_change, value=paint_page,
                                    text_align=ft.TextAlign.CENTER, input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""))

    lv = ft.ListView(spacing=1, padding=5)
    page.scroll = "always"

    # モーダルダイアログ
    def close_dlg_changed(e):
        dlg_modal.open = False
        key = dlg_modal.data
        deviation_value = dlg_modal.content._Row__controls[0].value
        deviation_page = dlg_modal.content._Row__controls[1].value
        if not deviation_value == "":
            deviation_value = int(deviation_value)
        if not deviation_page == "":
            deviation_page = int(deviation_page)
        else:
            deviation_page = 0
            # deviation_page = paint_page
        deviation_data[key] = [deviation_value, deviation_page]
        if deviation_value == 0 or deviation_value == "":
            del deviation_data[key]
        # print("add", deviation_data)
        refresh(page, lv, dlg_modal)

    def close_dlg(e):
        dlg_modal.open = False
        page.update()

    dlg_modal = ft.AlertDialog(
        modal=True,
        content=ft.Row([
            ft.TextField(label="偏移量(Y軸)", autofocus=True, width=130, input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string="")),
            ft.TextField(label="ページ数", width=90, input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string="")),
        ]),
        actions=[
            ft.TextButton("Yes", on_click=close_dlg_changed),
            ft.TextButton("No", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        # on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )

    page.add(screen_size, control_icons, paint_page_input, lv)

    while True:
        # suppress=True を設置することで、パソコンデフォルトのHotkeyの抑制可能
        keyboard.add_hotkey("f1", getMousePoint, args=[page, lv, dlg_modal], suppress=True)
        keyboard.add_hotkey("f2", getRGBColor, args=[page, lv, dlg_modal], suppress=True)
        keyboard.wait()

        # if keyboard.read_key(suppress=True) == "f1":
        #     getMousePoint(page, lv)
        # event = keyboard.read_event()
        # if event.name == 'f1':
        #     getMousePoint(page, lv, dlg_modal)
        # if event.name == 'f2':
        #     getRGBColor(page, lv, dlg_modal)
        # if event.name == 'end':
        #     page.window_destroy()
        # print(event)

ft.app(target=main)