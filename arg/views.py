import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Count

from .models import LorePage, PageScan, ContactSubmission


# ─── Данные дел архива ────────────────────────────────────────────────────────

CASES = [
    {
        'id': 'Z-001',
        'title': 'Инцидент на платформе 3',
        'date': '14.06.1962',
        'status': 'Закрыто',
        'status_cls': 'closed',
        'content': """
<p>В 04:17 утра дежурный по станции зафиксировал прибытие пассажирского состава,
не значившегося в расписании. Из вагонов вышли 12&nbsp;пассажиров. По прибытии
в журнал регистрации были внесены 13&nbsp;имён.</p>

<p>Расхождение объяснено ошибкой дежурного.<br>
Дежурный к утру следующего дня не вышел на смену.</p>

<p>Примечание архивариуса:<br>
Среди 12 вышедших пассажиров впоследствии один не смог объяснить, как он попал
на поезд. Он сообщил, что «ехал, чтобы встретить себя».</p>

<p class="stamp">ДЕЛО ЗАКРЫТО</p>
""",
        'hidden_text': None,
    },
    {
        'id': 'Z-002',
        'title': 'Потеря сигнала — Блок 7',
        'date': '02.03.1963',
        'status': 'Закрыто',
        'status_cls': 'closed',
        'content': """
<p>Оперативная группа зафиксировала полное прекращение радиосигнала на участке
Блок&nbsp;7 в промежутке 22:00–22:47. Технических причин установить не удалось.</p>
<p>Последняя запись в журнале дежурного содержит только цифры: 1, 1, 2, 3, 5, 8.</p>
<p class="stamp">ДЕЛО ЗАКРЫТО</p>
""",
        'hidden_text': None,
    },
    {
        'id': 'Z-003',
        'title': 'Объект без маршрута',
        'date': '17.09.1964',
        'status': 'Закрыто',
        'status_cls': 'closed',
        'content': """
<p>На перегоне между станциями «Архивная» и «Центральная» был зафиксирован состав
без бортового номера, следовавший в направлении, противоположном нормальному
движению по данному пути.</p>
<p>Состав не был задокументирован ни одной диспетчерской службой.</p>
<p class="stamp">ДЕЛО ЗАКРЫТО</p>
""",
        'hidden_text': None,
    },
    {
        'id': 'Z-004',
        'title': 'Показания свидетеля — А.&nbsp;Линдт',
        'date': '08.12.1965',
        'status': 'Закрыто',
        'status_cls': 'closed',
        'content': """
<p>Свидетель А.&nbsp;Линдт (58 лет) сообщил, что на протяжении трёх недель
наблюдал в окне своего кабинета силуэт, стоящий напротив здания в разное
время суток. При проверке в указанный момент — никого обнаружено не было.</p>
<p>Свидетель настаивал: «Он не стоит. Он ждёт.»</p>
<p>Дальнейшие показания прекратились по причинам, не подлежащим разглашению.</p>
<p class="stamp">ДЕЛО ЗАКРЫТО</p>
""",
        'hidden_text': None,
    },
    {
        'id': 'Z-005',
        'title': 'Аномалия расписания — сезон зима 1966',
        'date': '03.01.1967',
        'status': 'Закрыто',
        'status_cls': 'closed',
        'content': """
<p>В зимнем расписании 1966 года обнаружен рейс 14-04, не соответствующий
ни одному зарегистрированному маршруту. Рейс фигурирует в 12&nbsp;экземплярах
официального расписания, распространённых по сети станций.</p>
<p>Установить происхождение записи не удалось.</p>
<p class="stamp">ДЕЛО ЗАКРЫТО</p>
""",
        'hidden_text': None,
    },
    {
        'id': 'Z-006',
        'title': 'Исчезновение архивариуса — отдел Б',
        'date': '22.06.1969',
        'status': 'Закрыто',
        'status_cls': 'closed',
        'content': """
<p>Архивариус отдела Б не вышел на работу после того, как запросил доступ
к материалам дел Z-001 и Z-003 одновременно. Личные вещи остались на месте.
Записная книжка открыта на странице с одним словом: «считал».</p>
<p class="stamp">ДЕЛО ЗАКРЫТО</p>
""",
        'hidden_text': None,
    },
    {
        'id': 'Z-007',
        'title': 'Свидетельские показания: Е.&nbsp;Ковальский',
        'date': '03.11.1971',
        'status': 'Изъято',
        'status_cls': 'redacted',
        'content': """
<p>Гражданин Е.&nbsp;Ковальский сообщил, что в ходе командировки в г.&nbsp;Зателанд
встретил человека, который предъявил его собственные документы.</p>

<p>Цитата из показаний:</p>
<blockquote>«Он знал мой адрес. Мой настоящий адрес, который я не называл никому
с 1968&nbsp;года. Он знал, как зовут мою мать. Он знал, что я скажу это предложение
ещё до того, как я его сказал.»</blockquote>

<p>Дальнейшие показания <span class="redacted-inline">████████████████████████████</span></p>
<p>Местонахождение Е.&nbsp;Ковальского <span class="redacted-inline">████████████████</span></p>
<p class="stamp">СВИДЕТЕЛЬ НЕДОСТУПЕН // МАТЕРИАЛЫ ИЗЪЯТЫ</p>
""",
        'hidden_text': None,
    },
    {
        'id': 'Z-008',
        'title': 'Технический отчёт — камеры наблюдения',
        'date': '14.04.1974',
        'status': 'Закрыто',
        'status_cls': 'closed',
        'content': """
<p>Плановый технический осмотр камер наблюдения на станции Центральная выявил
аномалию: на 14 записях одного и того же дня зафиксированы люди, находившиеся
в двух местах одновременно.</p>
<p>Записи уничтожены в рамках регламента хранения.</p>
<p class="stamp">ДЕЛО ЗАКРЫТО</p>
""",
        'hidden_text': None,
    },
    {
        'id': 'Z-009',
        'title': 'Ошибка идентификации — Пост 12',
        'date': '07.08.1976',
        'status': 'Закрыто',
        'status_cls': 'closed',
        'content': """
<p>Дежурный поста №12 трижды обратился к одному и тому же пассажиру,
приняв его за трёх разных людей. Пассажир не предъявлял документов.</p>
<p>Дежурный после инцидента был направлен на медицинское освидетельствование.</p>
<p>Результаты освидетельствования <span class="redacted-inline">████████</span></p>
<p class="stamp">ДЕЛО ЗАКРЫТО</p>
""",
        'hidden_text': None,
    },
    {
        'id': 'Z-010',
        'title': 'Разрыв в журнале — 1977',
        'date': '01.01.1978',
        'status': 'Закрыто',
        'status_cls': 'closed',
        'content': """
<p>В журнале регистрации станции Зателанд обнаружен период с 11.04.1977
по 14.04.1977, в течение которого записи отсутствуют полностью.</p>
<p>Дежурные за указанный период не установлены.</p>
<p>Здание станции в указанный период, по данным смежных служб, функционировало
в штатном режиме.</p>
<p class="stamp">ДЕЛО ЗАКРЫТО</p>
""",
        'hidden_text': None,
    },
    {
        'id': 'Z-011',
        'title': 'Повторяющийся пассажир',
        'date': '19.02.1979',
        'status': 'Закрыто',
        'status_cls': 'closed',
        'content': """
<p>Кассир станции зафиксировала, что один и тот же мужчина приобрёл билет
на один и тот же маршрут 14&nbsp;раз за 14&nbsp;дней подряд. Внешность,
одежда и речь оставались идентичными.</p>
<p>На 15-й день мужчина не пришёл. На его месте у кассы стояла очередь
из людей с одинаковыми лицами.</p>
<p>Кассир ушла в отпуск. Не вернулась.</p>
<p class="stamp">ДЕЛО ЗАКРЫТО</p>
""",
        'hidden_text': None,
    },
    {
        'id': 'Z-014',
        'title': 'Расхождение пассажирских записей',
        'date': '22.02.1979',
        'status': 'Закрыто',
        'status_cls': 'closed',
        'content': """
<p>По итогам ревизии установлено, что количество пассажиров, зарегистрированных
при отправлении (47), не соответствует количеству пассажиров, зарегистрированных
при прибытии (48). Расхождение объяснено технической ошибкой регистрационного
аппарата.</p>

<p class="hidden-text">я зашёл в этот вагон один. я знаю, что я зашёл один. я считал. я всегда считаю. но когда я выходил, рядом со мной шёл я. он попросил меня не оборачиваться. я не обернулся. он живёт вместо меня уже одиннадцать лет. если ты читаешь это — пожалуйста, не считай людей в комнате.</p>

<p>Дальнейшая проверка признана нецелесообразной. Оборудование списано.</p>
<p class="stamp">ДЕЛО ЗАКРЫТО</p>
""",
        'hidden_text': True,
    },
    {
        'id': 'Z-022',
        'title': 'Аудиозапись №4-А',
        'date': '11.04.1987',
        'status': 'Закрыто',
        'status_cls': 'closed',
        'content': """
<p>В ходе плановой инвентаризации архива обнаружена аудиозапись,
не значащаяся ни в одном реестре. Маркировка катушки: «4-А / 14.04 / НЕ
ВОСПРОИЗВОДИТЬ».</p>

<p>Комиссия приняла решение о воспроизведении в контролируемых условиях.</p>

<p>Протокол прослушивания:</p>
<ul>
    <li>0:00–0:14 — тишина</li>
    <li>0:14–1:33 — неразборчивый голос, предположительно один говорящий</li>
    <li>1:33–1:34 — пауза</li>
    <li>1:34–1:35 — тот же голос, но с <em>другой стороны</em> комнаты</li>
    <li>1:35–конец — тишина</li>
</ul>

<p>Три члена комиссии отказались подписывать протокол. Причины не указаны.</p>

<p>Катушка <span class="redacted-inline">████████████████████</span></p>

<p class="stamp">ДЕЛО ЗАКРЫТО</p>
<p class="hidden-text-black">ты слышишь меня сейчас. ты думаешь, что это запись. это не запись. я говорю это в первый раз. ты читаешь это в первый раз. мы оба знаем, что это не так.</p>
""",
        'hidden_text': True,
        'hidden_type': 'black',
    },
    {
        'id': 'Z-031',
        'title': 'Объект «Подражатель»',
        'date': None,
        'status': 'На рассмотрении...',
        'status_cls': 'pending',
        'content': """
<p class="redacted-block">████████████████████████████████████████████████████████████</p>
<p class="redacted-block">████████████████████████████████████████████████████████████</p>

<p>Объект способен воспроизводить речевые паттерны, мимику и поведенческие
реакции целевого субъекта с точностью, <span class="redacted-inline">████████████████████████████████</span></p>

<p>Отличительные признаки объекта:</p>
<ul>
    <li>не инициирует визуальный контакт первым</li>
    <li>отвечает на вопросы с задержкой в 0,3–0,5 секунды</li>
    <li>не знает контрольного вопроса (см. Протокол 4-Б)</li>
    <li>при длительном наблюдении <span class="redacted-inline">████████████████</span></li>
</ul>

<p class="redacted-block">████████████████████████████████████████████████████████████</p>
<p class="stamp">НА РАССМОТРЕНИИ // ДАТА ИЗЪЯТА</p>
""",
        'hidden_text': None,
    },
]

CASES_MAP = {c['id']: c for c in CASES}

FIELD_REPORTS = [
    {
        'agent': 'Агент К.&nbsp;М.',
        'date': '19.08.1974',
        'status': 'вне связи',
        'status_cls': 'offline',
        'content': """
<p>Прибыл в Зателанд в 06:40. Разместился в гостинице «Центральная». Во время
первичного осмотра объекта наблюдения зафиксировал аномалию: объект двигался
в направлении, противоположном направлению взгляда.</p>
<p>Дальнейших донесений не поступало.</p>
""",
    },
    {
        'agent': 'Агент Е.&nbsp;Б.',
        'date': '02.05.1981',
        'status': 'вне связи',
        'status_cls': 'offline',
        'content': """
<p>Отчёт №3. Объект локализован. Повторяет мой маршрут с задержкой в 24&nbsp;часа.
Сегодня я зашёл в кафе у вокзала. Завтра он зайдёт туда же. Я заказал кофе
без сахара. Он закажет кофе без сахара.</p>
<p>Я не заказывал кофе без сахара.</p>
<p><em>Следующий отчёт не поступил.</em></p>
""",
    },
    {
        'agent': 'Агент N.',
        'date': '11.04.1987',
        'status': 'активен',
        'status_cls': 'active',
        'content': """
<p>Отчёт отправлен. Отчёт получен. Отчёт написан мной.</p>
<p>Я проверил. Это мой почерк. Моя подпись. Мой идентификационный код.</p>
<p>Я не писал этого отчёта.</p>
<p>Он уже был здесь, когда я сел за стол.</p>
<p>Если вы читаете это — значит, вы нашли то, что я спрятал внутри.
Не снаружи. Внутри.</p>
<p>Посмотрите внимательнее на /archive. На исходный код.</p>
<p>Он оставил след.</p>
""",
    },
]


# ─── Вспомогательные функции ──────────────────────────────────────────────────

def _get_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def _ensure_session(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


# ─── Views ────────────────────────────────────────────────────────────────────

def index(request):
    return render(request, 'arg/index.html')


def archive(request):
    # HTML-комментарий с подсказкой вшит в шаблон
    return render(request, 'arg/archive.html', {'cases': CASES})


def case_detail(request, case_id):
    case = CASES_MAP.get(case_id.upper())
    if not case:
        from django.http import Http404
        raise Http404
    return render(request, 'arg/case.html', {'case': case})


def cases(request):
    if 'cases' not in request.session.get('arg_unlocked', []):
        return render(request, 'arg/locked.html', {'section': 'CASES', 'act': 1})
    return render(request, 'arg/cases.html', {'reports': FIELD_REPORTS})


def protocols(request):
    if 'protocols' not in request.session.get('arg_unlocked', []):
        return render(request, 'arg/locked.html', {'section': 'PROTOCOLS', 'act': 2})
    return render(request, 'arg/protocols.html')


def about(request):
    return render(request, 'arg/about.html')


def observer(request):
    if 'observer' not in request.session.get('arg_unlocked', []):
        from django.http import Http404
        raise Http404
    return render(request, 'arg/observer.html')


def shadow(request):
    return render(request, 'arg/shadow.html')


def contact(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        agent_id = request.POST.get('agent_id', '').strip()
        ip = _get_ip(request)
        session_key = _ensure_session(request)

        triggered_special = False
        triggered_unlock = ''
        response_text = (
            'Запрос принят. Ответ будет направлен в течение 4–6 рабочих недель.'
        )

        # Проверка триггерной фразы
        if subject.lower() == settings.ARG_TRIGGER_PHRASE.lower():
            triggered_special = True
            response_text = (
                '[АВТООТВЕТ — СБОЙ ШАБЛОНА]\n\n'
                'да. я слышал тебя весь этот месяц.\n'
                'ты искал меня в коде, в белом тексте, в пустых страницах.\n'
                'я уже здесь. я был здесь, когда ты открыл сайт.\n\n'
                'посмотри в окно.\n\n'
                '[КОНЕЦ ПЕРЕДАЧИ]'
            )

        # Проверка кода разблокировки
        unlock_codes = getattr(settings, 'ARG_UNLOCK_CODES', {})
        if agent_id in unlock_codes:
            section = unlock_codes[agent_id]
            unlocked = list(request.session.get('arg_unlocked', []))
            if section not in unlocked:
                unlocked.append(section)
                request.session['arg_unlocked'] = unlocked
            triggered_unlock = section
            response_text = (
                f'Идентификатор принят. Доступ к разделу [{section.upper()}] открыт.\n'
                'Добро пожаловать, агент.'
            )

        ContactSubmission.objects.create(
            subject=subject,
            message=message,
            agent_id=agent_id,
            ip_address=ip,
            session_key=session_key,
            triggered_special=triggered_special,
            triggered_unlock=triggered_unlock,
        )

        return JsonResponse({'response': response_text, 'unlock': triggered_unlock})

    return render(request, 'arg/contact.html')


@login_required
def scan_log(request):
    pages = LorePage.objects.annotate(
        total_scans=Count('scans'),
        unique_visitors=Count('scans__session_key', distinct=True),
    ).order_by('created_at')

    recent_scans = PageScan.objects.select_related('page').order_by('-timestamp')[:200]
    contacts = ContactSubmission.objects.order_by('-timestamp')[:100]

    return render(request, 'arg/scan_log.html', {
        'pages': pages,
        'recent_scans': recent_scans,
        'contacts': contacts,
    })
