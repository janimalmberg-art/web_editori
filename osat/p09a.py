    # ================== TOIMINNOT ==================
    def create_actions(self):
        A = {}

        def mk(key, text, slot, shortcut=None):
            action = QAction(text, self)
            action.triggered.connect(slot)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            A[key] = action
            return action

        mk('new', '🆕 Uusi', self.new_page, 'Ctrl+N')
        mk('open', '📂 Avaa', self.open_file, 'Ctrl+O')
        mk('save', '💾 Tallenna', self.save_html, 'Ctrl+S')
        mk('save_xhtml', '💾 XHTML', self.save_xhtml, 'Ctrl+Shift+S')
        mk('save_pdf', '📄 PDF', self.save_pdf, 'Ctrl+P')
        mk('exit', '❌ Sulje', self.close, 'Ctrl+Q')

        mk('undo', '↶ Kumoa', lambda: self.fmt('undo'))
        mk('redo', '↷ Uudelleen', lambda: self.fmt('redo'))
        mk('clear_format', '🧹 Muotoilu pois', lambda: self.fmt('removeFormat'))

        mk('heading', '📝 Otsikko', self.add_heading, 'Ctrl+H')
        mk('paragraph', '¶ Kappale', self.add_paragraph)
        mk('bold', '𝐁 Lihavoi', lambda: self.fmt('bold'))
        mk('italic', '𝐼 Kursivoi', lambda: self.fmt('italic'))
        mk('underline', 'U Alleviivaa', lambda: self.fmt('underline'))
        mk('strike', 'S̶ Yliviivaa', lambda: self.fmt('strikeThrough'))
        mk('ul', '• Luettelo', lambda: self.fmt('insertUnorderedList'))
        mk('ol', '1. Numeroitu', lambda: self.fmt('insertOrderedList'))
        mk('align_left', '⬅ Vasen', lambda: self.fmt('justifyLeft'))
        mk('align_center', '⬌ Keskitä', lambda: self.fmt('justifyCenter'))
        mk('align_right', '➡ Oikea', lambda: self.fmt('justifyRight'))
        mk('align_justify', '≡ Molemmat', lambda: self.fmt('justifyFull'))

        mk('link', '🔗 Linkki', self.add_link)
        mk('unlink', '🔗✂ Ei linkkiä', lambda: self.fmt('unlink'))
        mk('image_file', '🖼 Kuva', self.add_image_file)
        mk('image_web', '🌐 Kuva verkosta', self.add_image_web)
        mk('table', '▦ Taulukko', self.add_table)
        mk('video', '▶ Video', self.add_video)
        mk('hr', '― Viiva', lambda: self._insert_html('<hr>'))
        mk('text_frame', '🗒 Tekstikehys', self.add_text_frame)
        mk('object_frame', '📊 Objektikehys', self.add_object_frame)
        mk('gallery', '🖼 Galleria', self.add_gallery)
        mk('calendar', '📅 Kalenteri', self.add_calendar)
        mk('nav_menu', '☰ Valikko', self.edit_nav_menu)
        mk('section', '📄 Osio', self.add_section)
        mk('php', '🐘 PHP', self.add_php_script)

        mk('color_text', '🎨 Tekstin väri', self.color_text)
        mk('color_bg', '🖍 Korostus', self.color_hilite)
        mk('color_elem', '🎨 Elementin väri', self.color_element)
        mk('color_elem_bg', '🎨 Elementin tausta', self.color_element_background)

        mk('move_up', '⬆ Ylös', self.move_up)
        mk('move_down', '⬇ Alas', self.move_down)
        mk('dup', '⧉ Kopioi', self.duplicate_block)
        mk('del', '🗑 Poista', self.delete_block)

        mk('settings', '⚙ Asetukset', self.page_settings)
        mk('update_preview', '➡ Päivitä esikatselu', self.update_preview)
        mk('update_code', '⬅ Päivitä koodi', self.update_code_from_preview)

        mk('help', '❓ Ohje', self.show_help)
        mk('info', 'ℹ Tietoja', self.show_info)

        for key in ('move_up', 'move_down', 'dup', 'del'):
            A[key].setEnabled(False)

        self.actions = A

        # ================== TYÖKALURIVIT ==================
        def bar(title):
            tb = QToolBar(title, self)
            tb.setMovable(False)
            self.addToolBar(tb)
            return tb

        tb1 = bar('Tiedosto ja muotoilu')
        for key in ('new', 'open', 'save', 'save_pdf'):
            tb1.addAction(A[key])
        tb1.addSeparator()
        for key in ('undo', 'redo', 'clear_format'):
            tb1.addAction(A[key])
        tb1.addSeparator()
        for key in ('heading', 'paragraph', 'bold', 'italic', 'underline', 'strike'):
            tb1.addAction(A[key])
        tb1.addSeparator()
        for key in ('ul', 'ol', 'align_left', 'align_center', 'align_right', 'align_justify'):
            tb1.addAction(A[key])

        tb2 = bar('Lisää sisältöä')
        for key in ('link', 'unlink', 'image_file', 'image_web', 'table', 'video', 'hr',
                    'text_frame', 'object_frame', 'gallery', 'calendar', 'section',
                    'nav_menu', 'php'):
            tb2.addAction(A[key])
        tb2.addSeparator()
        for key in ('color_text', 'color_bg', 'color_elem', 'color_elem_bg'):
            tb2.addAction(A[key])

        tb3 = bar('Sijoittelu ja sivu')
        for key in ('move_up', 'move_down', 'dup', 'del'):
            tb3.addAction(A[key])
        tb3.addSeparator()
        for key in ('settings', 'update_preview', 'update_code'):
            tb3.addAction(A[key])