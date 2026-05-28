import multiprocessing
import queue
import random
import time


def sensor_worker(sensor_queue, stop_event):
    """센서 값을 생성해 process-safe Queue에 전달한다."""
    print("센서 프로세스 시작")
    while not stop_event.is_set():
        data = random.uniform(0, 100)
        sensor_queue.put(data)
        time.sleep(0.05)
    print("센서 프로세스 종료")


def ai_inference_worker(sensor_queue, stop_event):
    """Queue에서 센서 값을 받아 무거운 추론 작업을 흉내 낸다."""
    print("AI 추론 프로세스 시작")
    while not stop_event.is_set() or not sensor_queue.empty():
        try:
            data = sensor_queue.get(timeout=0.2)
        except queue.Empty:
            continue

        print(f"[AI] 데이터 {data:.2f} 분석 중...")
        time.sleep(0.2)
        print("[AI] 결과: 장애물 없음")
    print("AI 추론 프로세스 종료")


def main():
    sensor_q = multiprocessing.Queue()
    stop_sig = multiprocessing.Event()

    sensor_process = multiprocessing.Process(
        target=sensor_worker,
        args=(sensor_q, stop_sig),
    )
    inference_processes = [
        multiprocessing.Process(target=ai_inference_worker, args=(sensor_q, stop_sig))
        for _ in range(2)
    ]

    sensor_process.start()
    for process in inference_processes:
        process.start()

    try:
        time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        stop_sig.set()
        sensor_process.join()
        for process in inference_processes:
            process.join()
        print("모든 시스템이 안전하게 종료되었습니다.")


if __name__ == "__main__":
    main()
