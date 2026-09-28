
def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Graafinen web-editori')
    win = HtmlEditor()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()