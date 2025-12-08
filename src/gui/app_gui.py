import PySimpleGUI as sg


class AppGUI:
    def __init__(self, log_queue):
        self.log_queue = log_queue
        self.window = None

    def _create_layout(self):
        layout = [
            [sg.Text('GeminiTrader - Stock Analysis', font=('Helvetica', 16, 'bold'), justification='center', expand_x=True)],
            [sg.Text('Status Log:')],
            [sg.Multiline(size=(80, 20), key='-LOG-', autoscroll=True, disabled=True, write_only=True)],
            [sg.Button('Run Now'), sg.Text('Next Scheduled Run: Not set', key='-NEXT-RUN-', size=(40, 1))],
        ]
        return layout

    def start_loop(self, scheduler_func, run_now_func):
        sg.theme('DefaultNoMoreNagging')
        layout = self._create_layout()
        self.window = sg.Window('GeminiTrader', layout, resizable=False, finalize=True)

        while True:
            event, values = self.window.read(timeout=100)

            if event == sg.WIN_CLOSED:
                break

            if event == 'Run Now':
                run_now_func()

            while not self.log_queue.empty():
                try:
                    log_message = self.log_queue.get_nowait()
                    self.window['-LOG-'].print(log_message)
                except:
                    break

            if scheduler_func:
                scheduler_func()

        self.window.close()

    def update_next_run(self, next_run_time):
        if self.window:
            self.window['-NEXT-RUN-'].update(f'Next Scheduled Run: {next_run_time}')
