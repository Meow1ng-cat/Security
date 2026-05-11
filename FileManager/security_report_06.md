Скриншот успешной XSS-атаки (до защиты).
Картинка с именем Task6_1

Пример кода функции-санитизера.

def sanitize_comment(raw_text: str) -> str:
    return bleach.clean(
        raw_text,
        tags=ALLOWED_TAGS,
        attributes={},
        strip=True,
        strip_comments=True
    )

Скриншот заголовков ответа (вкладка Network), где виден CSP.

Картинка с именем Task6_3

Скриншот заблокированной атаки (из консоли браузера).

Картинка с именем Task6_2

