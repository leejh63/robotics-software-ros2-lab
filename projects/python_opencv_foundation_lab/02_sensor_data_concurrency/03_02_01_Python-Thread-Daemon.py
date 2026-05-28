import threading
import time


def heartbeat():
    while True:
        print("Robot alive...")
        time.sleep(1.1)


def main():
    # daemon=True이면 메인 스레드 종료 시 백그라운드 스레드도 함께 종료된다.
    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()

    time.sleep(0.35)
    print("메인 프로그램 종료 -> 데몬 스레드 자동 종료")


if __name__ == "__main__":
    main()
