history = []

def calculator_with_history():
    """계산 기록을 저장하는 계산기"""
    while True:
        opr_ = input("+ - * / history q: ")

        match opr_:
            case "q":
                break
            case "history":
                if not history:
                    print("기록 없음")
                else:
                    for record in history:
                        print(record)
                continue
            case "+" | "-" | "*" | "/":
                pass  # 아래 계산 로직으로 진행
            case _:
                print(f"사용 가능: + - * / history q")
                continue

        try:
            num_1 = float(input("num_1: "))
            num_2 = float(input("num_2: "))
        except ValueError:
            print("숫자를 올바르게 입력해주세요")
            continue

        def plus():     return num_1 + num_2
        def minus():    return num_1 - num_2
        def multiple(): return num_1 * num_2
        def division():
            if num_2 == 0:
                raise ZeroDivisionError("0으로 나눌 수 없습니다")
            return num_1 / num_2

        mapping = {"+": plus, "-": minus, "*": multiple, "/": division}

        try:
            func = mapping.get(opr_)
            if func is None:
                print(f"지원하지 않는 연산자: {opr_}")
                continue
            result = func()
            record = f"{num_1} {opr_} {num_2} = {result}"
            history.append(record)
            print(f"결과: {result}")
        except ZeroDivisionError as e:
            print(e)


if __name__ == "__main__":
    calculator_with_history()