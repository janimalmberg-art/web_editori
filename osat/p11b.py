    # ================== SISÄLLÖN LISÄÄMINEN ==================
    def _image_frame_html(self, src, alt, caption):
        alt = html_mod.escape(alt or '', quote=True)
        src = str(src).replace('"', '&quot;')
        out = '<div class="image-frame">\n  <img src="%s" alt="%s">\n' % (src, alt)
        if caption:
            out += '  <div class="frame-caption">%s</div>\n' % html_mod.escape(caption)
        out += '</div>'
        return out

    def add_image_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Valitse kuva', '',
            'Kuvat (*.png *.jpg *.jpeg *.gif *.bmp *.webp *.svg)'
        )
        if not path:
            return
        try:
            with open(path, 'rb') as f:
                data = f.read()
        except Exception as e:
            QMessageBox.warning(self, 'Virhe', 'Kuvan lukeminen epäonnistui:\n%s' % e)
            return
        ext = os.path.splitext(path)[1].lower().lstrip('.')
        if ext == 'jpg':
            ext = 'jpeg'
        mime = {
            'png': 'image/png', 'jpeg': 'image/jpeg', 'gif': 'image/gif',
            'bmp': 'image/bmp', 'webp': 'image/webp', 'svg': 'image/svg+xml',
        }.get(ext, 'image/png')
        src = 'data:%s;base64,%s' % (mime, base64.b64encode(data).decode('ascii'))
        alt, _ = QInputDialog.getText(
            self, 'Kuva', 'Kuvaus (näkyy kuvan tilalla):', text=os.path.basename(path))
        caption, _ = QInputDialog.getText(self, 'Kuva', 'Kuvateksti (valinnainen):')
        self._insert_html(self._image_frame_html(src, alt or '', caption or ''))
        self.statusBar().showMessage('Kuva lisätty (upotettu sivutiedostoon)', 4000)

    def add_image_web(self):
        url, ok = QInputDialog.getText(
            self, 'Kuva verkosta', 'Kuvan osoite (URL):', text='https://'
        )
        if not ok or not url.strip():
            return
        alt, _ = QInputDialog.getText(self, 'Kuva verkosta', 'Kuvaus (alt-teksti):')
        caption, _ = QInputDialog.getText(
            self, 'Kuva verkosta', 'Kuvateksti (valinnainen):')
        self._insert_html(self._image_frame_html(url.strip(), alt or '', caption or ''))

    def add_table(self):
        dlg = TableDialog(self)
        if dlg.exec_() != QDialog.Accepted:
            return
        rows, cols, header, caption = dlg.get_data()
        out = ['<table class="data-table">']
        if caption:
            out.append('  <caption>%s</caption>' % html_mod.escape(caption))
        if header:
            out.append('  <tr>' +
                       ''.join('<th>Otsikko %d</th>' % (i + 1) for i in range(cols)) +
                       '</tr>')
            rows -= 1
        for _ in range(max(rows, 0)):
            out.append('  <tr>' + ''.join('<td>&nbsp;</td>' for _ in range(cols)) + '</tr>')
        out.append('</table>')
        self._insert_html('\n'.join(out))

    def add_video(self):
        url, ok = QInputDialog.getText(
            self, 'Video',
            'Videon osoite (YouTube-linkki tai suora .mp4/.webm-tiedosto):',
            text='https://'
        )
        if not ok or not url.strip():
            return
        url = url.strip()
        m = (re.search(r'youtube\.com/watch\?v=([\w-]{6,})', url)
             or re.search(r'youtu\.be/([\w-]{6,})', url))
        if m:
            vid = (
                '<div class="video-embed">\n'
                '  <iframe width="560" height="315" '
                'src="https://www.youtube.com/embed/%s" title="Video" frameborder="0" '
                'allow="accelerometer; autoplay; encrypted-media; gyroscope" '
                'allowfullscreen></iframe>\n</div>' % m.group(1)
            )
        elif re.search(r'\.(mp4|webm|ogv)(\?.*)?$', url, re.I):
            vid = (
                '<video controls style="max-width:100%%;">\n'
                '  <source src="%s">\n'
                '  Selaimesi ei tue videosoitinta.\n'
                '</video>'
            ) % url
        else:
            vid = (
                '<div class="video-embed">\n'
                '  <iframe width="560" height="315" src="%s" '
                'title="Upotettu sisältö" frameborder="0" allowfullscreen></iframe>\n</div>'
            ) % url
        self._insert_html(vid)