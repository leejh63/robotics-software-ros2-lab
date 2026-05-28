import queue
import random
import threading
import time


def producer(sensor_queue, stop_event):
    """0.1초마다 랜덤 센서 값을 생성해 Queue에 넣는다."""
    while not stop_event.is_set():
        value = round(random.uniform(0, 100), 2)
        sensor_queue.put(value)
        print(f"[Producer] 생성: {value}")
        time.sleep(0.1)


def consumer(sensor_queue, stop_event):
    """Queue에서 값을 꺼내 간단한 HIGH/LOW 판정을 출력한다."""
    while not stop_event.is_set() or not sensor_queue.empty():
        try:
            value = sensor_queue.get(timeout=0.2)
        except queue.Empty:
            continue

        result = "HIGH" if value >= 50 else "LOW"
        print(f"[Consumer] 처리: {value:.2f} -> 결과: {result} (큐 잔량: {sensor_queue.qsize()})")
        sensor_queue.task_done()


def main():
    sensor_queue = queue.Queue()
    stop_event = threading.Event()

    producer_thread = threading.Thread(target=producer, args=(sensor_queue, stop_event))
    consumer_thread = threading.Thread(target=consumer, args=(sensor_queue, stop_event))

    producer_thread.start()
    consumer_thread.start()

    try:
        time.sleep(3)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        producer_thread.join()
        consumer_thread.join()
        print("파이프라인 종료")


if __name__ == "__main__":
    main()
