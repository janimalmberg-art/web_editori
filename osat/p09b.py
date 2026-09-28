    # ================== VALIKOT ==================
    def create_menus(self):
        A = self.actions
        mb = self.menuBar()

        m_file = mb.addMenu('&Tiedosto')
        m_file.addAction(A['new'])
        m_file.addAction(A['open'])
        m_file.addSeparator()
        m_file.addAction(A['save'])
        m_file.addAction(A['save_xhtml'])
        m_file.addAction(A['save_pdf'])
        m_file.addSeparator()
        m_file.addAction(A['exit'])

        m_fmt = mb.addMenu('&Muotoilu')
        m_fmt.addAction(A['heading'])
        m_fmt.addAction(A['paragraph'])
        m_fmt.addSeparator()
        for key in ('bold', 'italic', 'underline', 'strike'):
            m_fmt.addAction(A[key])
        m_fmt.addSeparator()
        for key in ('ul', 'ol', 'align_left', 'align_center', 'align_right', 'align_justify'):
            m_fmt.addAction(A[key])
        m_fmt.addSeparator()
        m_fmt.addAction(A['clear_format'])
        m_fmt.addAction(A['color_text'])
        m_fmt.addAction(A['color_bg'])

        m_add = mb.addMenu('&Lisää')
        m_add.addAction(A['link'])
        m_add.addAction(A['unlink'])
        m_add.addSeparator()
        m_add.addAction(A['image_file'])
        m_add.addAction(A['image_web'])
        m_add.addSeparator()
        m_add.addAction(A['table'])
        m_add.addAction(A['video'])
        m_add.addAction(A['hr'])
        m_add.addSeparator()
        m_add.addAction(A['text_frame'])
        m_add.addAction(A['object_frame'])
        m_add.addSeparator()
        m_add.addAction(A['gallery'])
        m_add.addAction(A['calendar'])
        m_add.addSeparator()
        m_add.addAction(A['section'])
        m_add.addAction(A['nav_menu'])
        m_add.addSeparator()
        m_add.addAction(A['php'])

        m_layout = mb.addMenu('&Sijoittelu')
        for key in ('move_up', 'move_down', 'dup', 'del'):
            m_layout.addAction(A[key])

        m_colors = mb.addMenu('&Värit')
        for key in ('color_text', 'color_bg', 'color_elem', 'color_elem_bg'):
            m_colors.addAction(A[key])

        m_page = mb.addMenu('&Sivu')
        for key in ('settings', 'update_preview', 'update_code'):
            m_page.addAction(A[key])

        m_help = mb.addMenu('&Apua')
        m_help.addAction(A['help'])
        m_help.addAction(A['info'])