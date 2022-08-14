from beat_store import create_app

application = create_app()

if __name__ == '__main__':
    print('Run application.')
    application.run()