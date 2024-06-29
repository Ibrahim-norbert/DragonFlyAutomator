def main():
    import os
    data_path = os.path.abspath(__file__)
    os.chdir(os.path.dirname(data_path))

    import DragonFlyWellPlateAutomation.gui.MainWindow as application
    application.main()

if __name__ == '__main__':
    main()