from django.db import models


class LorePage(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="HTML разрешён")
    visible_hint = models.TextField(blank=True)
    hidden_clue = models.TextField(blank=True, help_text="Прячется в HTML-комментарий")
    is_secret = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'[SECRET] ' if self.is_secret else ''}{self.title} (/{self.slug})"

    class Meta:
        verbose_name = "Страница лора"
        verbose_name_plural = "Страницы лора"


class PageScan(models.Model):
    page = models.ForeignKey(LorePage, on_delete=models.CASCADE, related_name="scans")
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=64, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_first_visit = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.ip_address} → /{self.page.slug} в {self.timestamp:%d.%m.%Y %H:%M}"

    class Meta:
        verbose_name = "Скан / посещение"
        verbose_name_plural = "Сканы / посещения"
        ordering = ["-timestamp"]


class ContactSubmission(models.Model):
    subject = models.CharField(max_length=500, blank=True)
    message = models.TextField(blank=True)
    agent_id = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=64, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    triggered_special = models.BooleanField(default=False, help_text="Ввёл ключевую фразу")
    triggered_unlock = models.CharField(max_length=100, blank=True, help_text="Какой акт разблокировал")

    def __str__(self):
        flag = " [SPECIAL]" if self.triggered_special else ""
        unlock = f" [UNLOCK:{self.triggered_unlock}]" if self.triggered_unlock else ""
        return f"{self.ip_address} — «{self.subject[:40]}»{flag}{unlock} — {self.timestamp:%d.%m.%Y %H:%M}"

    class Meta:
        verbose_name = "Обращение через форму"
        verbose_name_plural = "Обращения через форму"
        ordering = ["-timestamp"]
